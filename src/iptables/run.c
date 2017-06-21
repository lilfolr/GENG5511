#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <netdb.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ip_tables.h"



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
int main(int argc, char* argv[]){
    printf("Starting\n");
    struct sk_buff *packet;
    
    printf("Making sk_buff\n");
    packet = (struct sk_buff) malloc(sizeof(struct iphdr) + sizeof(struct icmphdr)); //TODO: FIx;

    packet->next = void;
    packet->prev = void;
    
    printf("Making nf_hook_state\n");

    printf("Making xt_table\n");

    bool packet_pass;
    struct iphdr *ip;
    char *dst_addr="192.168.1.2";
    char *src_addr="192.168.1.3";
    ip = (struct iphdr*) malloc(sizeof(struct iphdr) + sizeof(struct icmphdr));
    ip->ihl         = 5;
    ip->version     = 4;
    ip->tot_len     = sizeof(struct iphdr) + sizeof(struct icmphdr);
    ip->protocol    = IPPROTO_ICMP;
    ip->saddr       = inet_addr(src_addr);
    ip->daddr       = inet_addr(dst_addr);
    ip->check = in_cksum((unsigned short *)ip, sizeof(struct iphdr)); 

    //The rule
    struct ipt_ip *ipinfo;
    ipinfo = (struct ipt_ip*) malloc(sizeof(struct ipt_ip));
    ipinfo->proto   = 0;  //Protocol. 0=Any
    ipinfo->src     = get_in_addr(ip->saddr);
    ipinfo->dst     = get_in_addr(ip->daddr);
    //SEE REF_FLAGS Below
    //ipinfo->flags
    //ipinfo->invflags
    ipinfo->smsk    = get_in_addr(inet_addr("255.255.255.255"));
    ipinfo->dmsk    = get_in_addr(inet_addr("255.255.255.255"));
    // ipinfo->iniface
    // ipinfo->outiface
    // ipinfo->iniface_mask
    // ipinfo->outiface_mask

    char* indev = "eth0";
    char* outdev = "eth0";

    packet_pass = ip_packet_match(ip, indev, outdev, ipinfo, false);
    printf("Result: ");
    printf(packet_pass ? "True\n" : "False\n");
    printf("End\n");
}
/* REF_FLAGS
// /* Values for "flag" field in struct ipt_ip (general ip structure). */
// #define IPT_F_FRAG		0x01	/* Set if rule is a fragment rule */
// #define IPT_F_GOTO		0x02	/* Set if jump is a goto */
// #define IPT_F_MASK		0x03	/* All possible flag bits mask. */

// /* Values for "inv" field in struct ipt_ip. */
// #define IPT_INV_VIA_IN		0x01	/* Invert the sense of IN IFACE. */
// #define IPT_INV_VIA_OUT		0x02	/* Invert the sense of OUT IFACE */
// #define IPT_INV_TOS		    0x04	/* Invert the sense of TOS. */
// #define IPT_INV_SRCIP		0x08	/* Invert the sense of SRC IP. */
// #define IPT_INV_DSTIP		0x10	/* Invert the sense of DST OP. */
// #define IPT_INV_FRAG		    0x20	/* Invert the sense of FRAG. */
// #define IPT_INV_PROTO		XT_INV_PROTO
// #define IPT_INV_MASK		    0x7F	/* All possible flag bits mask. */


// Function Definitions:
// bool ip_packet_match(
//      const struct iphdr *ip,
// 		const char *indev,
// 		const char *outdev,
// 		const struct ipt_ip *ipinfo,
// 		int isfrag
//      );
// ------------------------------------------------
// unsigned int ipt_do_table(
//      struct sk_buff *skb,
// 	    const struct nf_hook_state *state,
// 	    struct xt_table *table
//      );

// sk_buff structure
// struct sk_buff {
//   struct sk_buff * next;
//   struct sk_buff * prev;
//   struct sock * sk;
//   struct skb_timeval tstamp;
//   struct net_device * dev;
//   struct net_device * input_dev;
//   union h;
//   union nh;
//   union mac;
//   struct dst_entry * dst;
//   struct sec_path * sp;
//   char cb[48];
//   unsigned int len;
//   unsigned int data_len;
//   unsigned int mac_len;
//   unsigned int csum;
//   __u32 priority;
//   __u8 local_df:1;
//   __u8 cloned:1;
//   __u8 ip_summed:2;
//   __u8 nohdr:1;
//   __u8 nfctinfo:3;
//   __u8 pkt_type:3;
//   __u8 fclone:2;
//   __u8 ipvs_property:1;
//   __be16 protocol;
//   void (* destructor) (struct sk_buff *skb);
// #ifdef CONFIG_NETFILTER
//   struct nf_conntrack * nfct;
// #if defined(CONFIG_NF_CONNTRACK) || defined(CONFIG_NF_CONNTRACK_MODULE)
//   struct sk_buff * nfct_reasm;
// #endif
// #ifdef CONFIG_BRIDGE_NETFILTER
//   struct nf_bridge_info * nf_bridge;
// #endif
//   __u32 nfmark;
// #endif
// #ifdef CONFIG_NET_SCHED
//   __u16 tc_index;
// #ifdef CONFIG_NET_CLS_ACT
//   __u16 tc_verd;
// #endif
// #endif
// #ifdef CONFIG_NET_DMA
//   dma_cookie_t dma_cookie;
// #endif
// #ifdef CONFIG_NETWORK_SECMARK
//   __u32 secmark;
// #endif
//   unsigned int truesize;
//   atomic_t users;
//   unsigned char * head;
//   unsigned char * data;
//   unsigned char * tail;
//   unsigned char * end;
// }; 
