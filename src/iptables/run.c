//Define a macro that returns true when bool and invflg are true. 
//Note that the purpose of using two "!" Here is to make the calculated values only take values of 0 and 1
#define NF_INVF(ptr, flag, boolean)					\
	((boolean) ^ !!((ptr)->invflags & (flag)))
    
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ip_tables.c"

static struct in_addr get_in_addr(__be32 addr){
    struct in_addr ret;
    ret.s_addr = addr;
    return ret;
}

unsigned short in_cksum(unsigned short *addr, int len)
{
    register int sum = 0;
    u_short answer = 0;
    register u_short *w = addr;
    register int nleft = len;
    /*
     * Our algorithm is simple, using a 32 bit accumulator (sum), we add
     * sequential 16 bit words to it, and at the end, fold back all the
     * carry bits from the top 16 bits into the lower 16 bits.
     */
    while (nleft > 1)
    {
      sum += *w++;
      nleft -= 2;
    }
    /* mop up an odd byte, if necessary */
    if (nleft == 1)
    {
      *(u_char *) (&answer) = *(u_char *) w;
      sum += answer;
    }
    /* add back carry outs from top 16 bits to low 16 bits */
    sum = (sum >> 16) + (sum & 0xffff);     /* add hi 16 to low 16 */
    sum += (sum >> 16);             /* add carry */
    answer = ~sum;              /* truncate to 16 bits */
    return (answer);
}

// Input struct for defining our packet
typedef struct in_packets{
    int ttl;
	int protocol;
	char* dst_addr;
	char* src_addr;
} in_packet;

// Input struct for defining our rule
typedef struct in_rules{
	int protocol;
	char* src_addr;
	char* dst_addr;
	char* indev;
	char* outdev;
} in_rule;

// Takes a packet and a rule, and returns True if they match, and False if not
int run_sim(in_packet *packet, in_rule *rule){
    printf("Starting\n");
    bool packet_pass;

    //The Packet
    struct iphdr *ip;
    char *dst_addr="192.168.1.2";
    char *src_addr="192.168.1.3";

    // This is just for icmp - the simplest of packets :)
    ip = (struct iphdr*) malloc(sizeof(struct iphdr) + sizeof(struct icmphdr)); 
    ip->ihl         = 4;                                                        // ip header length - always 4 bits
    ip->version     = 4;                                                        // Always 4 [IPv4 i think]
    ip->tot_len     = sizeof(struct iphdr) + sizeof(struct icmphdr);
    ip->protocol    = IPPROTO_ICMP;                                             // See 3.0 below
    ip->saddr       = inet_addr(packet->src_addr);
    ip->daddr       = inet_addr(packet->dst_addr);
    ip->check = in_cksum((unsigned short *)ip, sizeof(struct iphdr)); 
    ip->ttl = packet->ttl;                                                      // Time to live
    
    //The rule
    char* indev = "eth1";
    char* outdev = "eth1";
    // const unsigned long mask[4] = {1,1,1,1};
    // const char *_mask =  (const char *) mask;
    
    struct ipt_ip *ipinfo;
    ipinfo = (struct ipt_ip*) malloc(sizeof(struct ipt_ip));
    ipinfo->proto   = 0;  //Protocol. 0=Any
    ipinfo->src     = get_in_addr(inet_addr(src_addr));
    ipinfo->dst     = get_in_addr(inet_addr(dst_addr));
    //SEE REF_FLAGS Below
    //ipinfo->flags
    ipinfo->invflags = IPT_INV_VIA_IN | IPT_INV_VIA_OUT; //Don't care about interface matching
    ipinfo->smsk    = get_in_addr(inet_addr("255.255.255.255"));
    ipinfo->dmsk    = get_in_addr(inet_addr("255.255.255.255"));
    // strcpy(ipinfo->iniface, "eth2");
    // strcpy(ipinfo->outiface,"eth2");
    // strcpy(ipinfo->iniface_mask,_mask);
    // strcpy(ipinfo->outiface_mask,_mask);


    packet_pass = ip_packet_match(ip, indev, outdev, ipinfo, false);
    printf("Result: ");
    printf(packet_pass ? "True\n" : "False\n");
    printf("End");
}


// /* 1.0 REF_FLAGS
// /* Values for "flag" field in struct ipt_ip (general ip structure). */
// #define IPT_F_FRAG		0x01	/* Set if rule is a fragment rule */
// #define IPT_F_GOTO		0x02	/* Set if jump is a goto */
// #define IPT_F_MASK		0x03	/* All possible flag bits mask. */

// /* 2.0 Values for "inv" field in struct ipt_ip. */
// #define IPT_INV_VIA_IN		0x01	/* Invert the sense of IN IFACE. */
// #define IPT_INV_VIA_OUT		0x02	/* Invert the sense of OUT IFACE */
// #define IPT_INV_TOS		    0x04	/* Invert the sense of TOS. */
// #define IPT_INV_SRCIP		0x08	/* Invert the sense of SRC IP. */
// #define IPT_INV_DSTIP		0x10	/* Invert the sense of DST OP. */
// #define IPT_INV_FRAG		    0x20	/* Invert the sense of FRAG. */
// #define IPT_INV_PROTO		XT_INV_PROTO
// #define IPT_INV_MASK		    0x7F	/* All possible flag bits mask. */

// /* 3.0 Standard well-defined IP protocols.  */
//   IPPROTO_IP = 0,		/* Dummy protocol for TCP		*/
//   IPPROTO_ICMP = 1,		/* Internet Control Message Protocol	*/
//   IPPROTO_IGMP = 2,		/* Internet Group Management Protocol	*/
//   IPPROTO_IPIP = 4,		/* IPIP tunnels (older KA9Q tunnels use 94) */
//   IPPROTO_TCP = 6,		/* Transmission Control Protocol	*/
//   IPPROTO_EGP = 8,		/* Exterior Gateway Protocol		*/
//   IPPROTO_PUP = 12,		/* PUP protocol				*/
//   IPPROTO_UDP = 17,		/* User Datagram Protocol		*/
//   IPPROTO_IDP = 22,		/* XNS IDP protocol			*/
//   IPPROTO_TP = 29,		/* SO Transport Protocol Class 4	*/
//   IPPROTO_DCCP = 33,		/* Datagram Congestion Control Protocol */
//   IPPROTO_IPV6 = 41,		/* IPv6-in-IPv4 tunnelling		*/
//   IPPROTO_RSVP = 46,		/* RSVP Protocol			*/
//   IPPROTO_GRE = 47,		/* Cisco GRE tunnels (rfc 1701,1702)	*/
//   IPPROTO_ESP = 50,		/* Encapsulation Security Payload protocol */
//   IPPROTO_AH = 51,		/* Authentication Header protocol	*/
//   IPPROTO_MTP = 92,		/* Multicast Transport Protocol		*/
//   IPPROTO_BEETPH = 94,	/* IP option pseudo header for BEET	*/
//   IPPROTO_ENCAP = 98,	/* Encapsulation Header			*/
//   IPPROTO_PIM = 103,		/* Protocol Independent Multicast	*/
//   IPPROTO_COMP = 108,	/* Compression Header Protocol		*/
//   IPPROTO_SCTP = 132,	/* Stream Control Transport Protocol	*/
//   IPPROTO_UDPLITE = 136,	/* UDP-Lite (RFC 3828)			*/
//   IPPROTO_MPLS = 137,	/* MPLS in IP (RFC 4023)		*/
//   IPPROTO_RAW = 255,		/* Raw IP packets			*/