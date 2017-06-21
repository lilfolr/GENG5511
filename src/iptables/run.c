#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <netdb.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ip_tables.h"
#include <linux/netdevice.h>
#include <linux/ip.h>

#define LL_MAX_HEADER 128

#define __GFP_HIGH		0x20u
#define __GFP_ATOMIC		0x80000u
#define __GFP_KSWAPD_RECLAIM	0x2000000u
#define GFP_ATOMIC	(__GFP_HIGH|__GFP_ATOMIC|__GFP_KSWAPD_RECLAIM)

/* IP flags. */
#define IP_CE		0x8000		/* Flag: "Congestion"		*/
#define IP_DF		0x4000		/* Flag: "Don't Fragment"	*/
#define IP_MF		0x2000		/* Flag: "More Fragments"	*/
#define IP_OFFSET	0x1FFF		/* "Fragment Offset" part	*/

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
    struct iphdr *newip;
    //struct udphdr *newudp;

    printf("Making sk_buff\n");
    packet = alloc_skb(LL_MAX_HEADER + sizeof(struct iphdr*) + 0x08 + 0x00, GFP_ATOMIC); //https://ubuntuforums.org/showthread.php?t=1852227

	if (skb_linearize(packet) < 0)
        return NF_DROP;
    skb_reserve(packet, LL_MAX_HEADER); //skb_reserve sets the data pointer, and re-zeros the tail

	skb_reset_network_header(packet);

    newip = (void *)skb_put(packet, sizeof(struct iphdr*)); //skb_put sets the tail for iphdr
    newip->version  = IPVERSION;
    newip->ihl      = sizeof(struct iphdr) / 4;
    newip->tos      = 0;
    newip->id       = 0;
    newip->frag_off = htons(IP_DF);
    newip->protocol = IPPROTO_UDP;
    newip->check    = 0;
    newip->saddr    = htonl(0xC0A80101);
    newip->daddr    = htonl(0xC0A80102);

//    newudp = (void *)skb_put(packet, sizeof(struct udphdr)); //skb_put re-sets the tail for udphdr
//
//    newudp->source = htons(0x1234); //4660
//    newudp->dest   = htons(0x1235); //4661
//    newudp->len    = htons(sizeof(struct udphdr));
//    newudp->check  = 0;



    printf("Making nf_hook_state\n");
//    struct nf_hook_state {
//    	unsigned int hook;
//    	u_int8_t pf;
//    	struct net_device *in;
//    	struct net_device *out;
//    	struct sock *sk;
//    	struct net *net;
//    	int (*okfn)(struct net *, struct sock *, struct sk_buff *);
//    }
//	nf_inet_hooks
//		NF_INET_PRE_ROUTING,
//		NF_INET_LOCAL_IN,
//		NF_INET_FORWARD,
//		NF_INET_LOCAL_OUT,
//		NF_INET_POST_ROUTING,
//		NF_INET_NUMHOOKS
	enum {
		NFPROTO_UNSPEC =  0,
		NFPROTO_INET   =  1,
		NFPROTO_IPV4   =  2,
		NFPROTO_ARP    =  3,
		NFPROTO_NETDEV =  5,
		NFPROTO_BRIDGE =  7,
		NFPROTO_IPV6   = 10,
		NFPROTO_DECNET = 12,
		NFPROTO_NUMPROTO,
	};

    const struct nf_hook_state *state;
    nf_hook_state_init(&state, NF_INET_LOCAL_IN, NFPROTO_IPV4,packet->dev, NULL, NULL,dev_net(packet->dev), NULL);

    printf("Making xt_table\n");



	int result;
    //result = ipt_do_table(packet, state, newinfo); // ipt_do_table(struct sk_buff *skb,const struct nf_hook_state *state,struct xt_table *table);
    printf("Result: %d",result);
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
