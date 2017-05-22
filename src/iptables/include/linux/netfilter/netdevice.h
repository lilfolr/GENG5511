#include <linux/types.h>

#define	IFNAMSIZ	16
#define MAX_ADDR_LEN	32		
#define TC_MAX_QUEUE	16
#define TC_BITMASK	15
#define spinlock_t		pthread_mutex_t
#define ____cacheline_aligned_in_smp __attribute__ ((aligned (64))) //64=L1 cache bytes
# define __percpu	__attribute__((noderef, address_space(3)))
# define __rcu		__attribute__((noderef, address_space(4)))
struct callback_head {
	struct callback_head *next;
	void (*func)(struct callback_head *head);
} __attribute__((aligned(sizeof(void *))));
#define rcu_head callback_head
#define DIV_ROUND_UP(n, d) (((n) + (d) - 1) / (d))
// #define BITS_TO_LONGS(nr)	DIV_ROUND_UP(nr, 8 * sizeof(long))
// #define DECLARE_BITMAP(name,bits) \
// unsigned long name[BITS_TO_LONGS(bits)]

// Types
typedef int64_t s64;
typedef uint64_t u64;
typedef __u32 u32;
typedef unsigned int sk_buff_data_t;
typedef u64 netdev_features_t;
typedef struct {
	int counter;
} atomic_t;
typedef struct {
	long counter;
} atomic64_t;
typedef struct {
#ifdef CONFIG_NET_NS
	struct net *net;
#endif
} possible_net_t;
typedef atomic64_t atomic_long_t;
typedef enum rx_handler_result rx_handler_result_t;
typedef rx_handler_result_t rx_handler_func_t(struct sk_buff **pskb);

#ifndef IPV4_DEVCONF_MAX
/* index values for the variables in ipv4_devconf */
enum
{
	IPV4_DEVCONF_FORWARDING=1,
	IPV4_DEVCONF_MC_FORWARDING,
	IPV4_DEVCONF_PROXY_ARP,
	IPV4_DEVCONF_ACCEPT_REDIRECTS,
	IPV4_DEVCONF_SECURE_REDIRECTS,
	IPV4_DEVCONF_SEND_REDIRECTS,
	IPV4_DEVCONF_SHARED_MEDIA,
	IPV4_DEVCONF_RP_FILTER,
	IPV4_DEVCONF_ACCEPT_SOURCE_ROUTE,
	IPV4_DEVCONF_BOOTP_RELAY,
	IPV4_DEVCONF_LOG_MARTIANS,
	IPV4_DEVCONF_TAG,
	IPV4_DEVCONF_ARPFILTER,
	IPV4_DEVCONF_MEDIUM_ID,
	IPV4_DEVCONF_NOXFRM,
	IPV4_DEVCONF_NOPOLICY,
	IPV4_DEVCONF_FORCE_IGMP_VERSION,
	IPV4_DEVCONF_ARP_ANNOUNCE,
	IPV4_DEVCONF_ARP_IGNORE,
	IPV4_DEVCONF_PROMOTE_SECONDARIES,
	IPV4_DEVCONF_ARP_ACCEPT,
	IPV4_DEVCONF_ARP_NOTIFY,
	IPV4_DEVCONF_ACCEPT_LOCAL,
	IPV4_DEVCONF_SRC_VMARK,
	IPV4_DEVCONF_PROXY_ARP_PVLAN,
	IPV4_DEVCONF_ROUTE_LOCALNET,
	IPV4_DEVCONF_IGMPV2_UNSOLICITED_REPORT_INTERVAL,
	IPV4_DEVCONF_IGMPV3_UNSOLICITED_REPORT_INTERVAL,
	IPV4_DEVCONF_IGNORE_ROUTES_WITH_LINKDOWN,
	IPV4_DEVCONF_DROP_UNICAST_IN_L2_MULTICAST,
	IPV4_DEVCONF_DROP_GRATUITOUS_ARP,
	__IPV4_DEVCONF_MAX
};
#endif

#define IPV4_DEVCONF_MAX (__IPV4_DEVCONF_MAX - 1)

struct device;
struct list_head {
	struct list_head *next, *prev;
};
struct netdev_hw_addr_list {
	struct list_head	list;
	int			count;
};
struct hlist_node {
	struct hlist_node *next, **pprev;
};
struct timer_list {
	/*
	 * All fields that change during normal runtime grouped to the
	 * same cacheline
	 */
	struct hlist_node	entry;
	unsigned long		expires;
	void			(*function)(unsigned long);
	unsigned long		data;
	u32			flags;
#ifdef CONFIG_LOCKDEP
	struct lockdep_map	lockdep_map;
#endif
};
struct net_device_stats {
	unsigned long	rx_packets;
	unsigned long	tx_packets;
	unsigned long	rx_bytes;
	unsigned long	tx_bytes;
	unsigned long	rx_errors;
	unsigned long	tx_errors;
	unsigned long	rx_dropped;
	unsigned long	tx_dropped;
	unsigned long	multicast;
	unsigned long	collisions;
	unsigned long	rx_length_errors;
	unsigned long	rx_over_errors;
	unsigned long	rx_crc_errors;
	unsigned long	rx_frame_errors;
	unsigned long	rx_fifo_errors;
	unsigned long	rx_missed_errors;
	unsigned long	tx_aborted_errors;
	unsigned long	tx_carrier_errors;
	unsigned long	tx_fifo_errors;
	unsigned long	tx_heartbeat_errors;
	unsigned long	tx_window_errors;
	unsigned long	rx_compressed;
	unsigned long	tx_compressed;
};
struct netdev_tc_txq {
	__u16 count;
	__u16 offset;
};
struct ip_mc_list {
	struct in_device	*interface;
	__be32			multiaddr;
	unsigned int		sfmode;
	struct ip_sf_list	*sources;
	struct ip_sf_list	*tomb;
	unsigned long		sfcount[2];
	union {
		struct ip_mc_list *next;
		struct ip_mc_list __rcu *next_rcu;
	};
	struct ip_mc_list __rcu *next_hash;
	struct timer_list	timer;
	int			users;
	atomic_t		refcnt;
	spinlock_t		lock;
	char			tm_running;
	char			reporter;
	char			unsolicit_count;
	char			loaded;
	unsigned char		gsquery;	/* check source marks? */
	unsigned char		crcount;
	struct rcu_head		rcu;
};
struct ipv4_devconf {
	void	*sysctl;
	
	int	data[IPV4_DEVCONF_MAX];
	unsigned long state[DIV_ROUND_UP(IPV4_DEVCONF_MAX, 8 * sizeof(long))]
};
struct in_device {
	struct net_device	*dev;
	atomic_t		refcnt;
	int			dead;
	struct in_ifaddr	*ifa_list;	/* IP ifaddr chain		*/

	struct ip_mc_list __rcu	*mc_list;	/* IP multicast filter chain    */
	struct ip_mc_list __rcu	* __rcu *mc_hash;

	int			mc_count;	/* Number of installed mcasts	*/
	spinlock_t		mc_tomb_lock;
	struct ip_mc_list	*mc_tomb;
	unsigned long		mr_v1_seen;
	unsigned long		mr_v2_seen;
	unsigned long		mr_maxdelay;
	unsigned char		mr_qrv;
	unsigned char		mr_gq_running;
	unsigned char		mr_ifc_count;
	struct timer_list	mr_gq_timer;	/* general query timer */
	struct timer_list	mr_ifc_timer;	/* interface change timer */

	struct neigh_parms	*arp_parms;
	struct ipv4_devconf	cnf;
	struct rcu_head		rcu_head;
};

struct netdev_queue {
	struct net_device	*dev;
	struct Qdisc __rcu	*qdisc;
	struct Qdisc		*qdisc_sleeping;
#ifdef CONFIG_SYSFS
	struct kobject		kobj;
#endif
#if defined(CONFIG_XPS) && defined(CONFIG_NUMA)
	int			numa_node;
#endif
	unsigned long		tx_maxrate;
	unsigned long		trans_timeout;
	spinlock_t		_xmit_lock ____cacheline_aligned_in_smp;
	int			xmit_lock_owner;
	unsigned long		trans_start;
	unsigned long		state;
#ifdef CONFIG_BQL
	struct dql		dql;
#endif
} ____cacheline_aligned_in_smp;
struct net_device {
	char			name[IFNAMSIZ];
	struct hlist_node	name_hlist;
	char 			*ifalias;
	/*
	 *	I/O specific fields
	 *	FIXME: Merge these and struct ifmap into one
	 */
	unsigned long		mem_end;
	unsigned long		mem_start;
	unsigned long		base_addr;
	int			irq;

	atomic_t		carrier_changes;

	/*
	 *	Some hardware also needs these fields (state,dev_list,
	 *	napi_list,unreg_list,close_list) but they are not
	 *	part of the usual set specified in Space.c.
	 */

	unsigned long		state;

	struct list_head	dev_list;
	struct list_head	napi_list;
	struct list_head	unreg_list;
	struct list_head	close_list;
	struct list_head	ptype_all;
	struct list_head	ptype_specific;

	struct {
		struct list_head upper;
		struct list_head lower;
	} adj_list;

	netdev_features_t	features;
	netdev_features_t	hw_features;
	netdev_features_t	wanted_features;
	netdev_features_t	vlan_features;
	netdev_features_t	hw_enc_features;
	netdev_features_t	mpls_features;
	netdev_features_t	gso_partial_features;

	int			ifindex;
	int			group;

	struct net_device_stats	stats;

	atomic_long_t		rx_dropped;
	atomic_long_t		tx_dropped;
	atomic_long_t		rx_nohandler;

#ifdef CONFIG_WIRELESS_EXT
	const struct iw_handler_def *wireless_handlers;
	struct iw_public_data	*wireless_data;
#endif
	const struct net_device_ops *netdev_ops;
	const struct ethtool_ops *ethtool_ops;
#ifdef CONFIG_NET_SWITCHDEV
	const struct switchdev_ops *switchdev_ops;
#endif
#ifdef CONFIG_NET_L3_MASTER_DEV
	const struct l3mdev_ops	*l3mdev_ops;
#endif
	const struct ndisc_ops *ndisc_ops;
#ifdef CONFIG_XFRM
	const struct xfrmdev_ops *xfrmdev_ops;
#endif

	const struct header_ops *header_ops;

	unsigned int		flags;
	unsigned int		priv_flags;

	unsigned short		gflags;
	unsigned short		padded;

	unsigned char		operstate;
	unsigned char		link_mode;

	unsigned char		if_port;
	unsigned char		dma;

	unsigned int		mtu;
	unsigned int		min_mtu;
	unsigned int		max_mtu;
	unsigned short		type;
	unsigned short		hard_header_len;
	unsigned char		min_header_len;

	unsigned short		needed_headroom;
	unsigned short		needed_tailroom;

	/* Interface address info. */
	unsigned char		perm_addr[MAX_ADDR_LEN];
	unsigned char		addr_assign_type;
	unsigned char		addr_len;
	unsigned short		neigh_priv_len;
	unsigned short          dev_id;
	unsigned short          dev_port;
	spinlock_t		addr_list_lock;
	unsigned char		name_assign_type;
	bool			uc_promisc;
	struct netdev_hw_addr_list	uc;
	struct netdev_hw_addr_list	mc;
	struct netdev_hw_addr_list	dev_addrs;

#ifdef CONFIG_SYSFS
	struct kset		*queues_kset;
#endif
	unsigned int		promiscuity;
	unsigned int		allmulti;


	/* Protocol-specific pointers */

	void 			*atalk_ptr;
	struct in_device __rcu	*ip_ptr;
	struct dn_dev __rcu     *dn_ptr;
	struct inet6_dev __rcu	*ip6_ptr;
	void			*ax25_ptr;
	struct wireless_dev	*ieee80211_ptr;
	struct wpan_dev		*ieee802154_ptr;

/*
 * Cache lines mostly used on receive path (including eth_type_trans())
 */
	/* Interface address info used in eth_type_trans() */
	unsigned char		*dev_addr;

#ifdef CONFIG_SYSFS
	struct netdev_rx_queue	*_rx;

	unsigned int		num_rx_queues;
	unsigned int		real_num_rx_queues;
#endif

	struct bpf_prog __rcu	*xdp_prog;
	unsigned long		gro_flush_timeout;
	rx_handler_func_t __rcu	*rx_handler;
	void __rcu		*rx_handler_data;

#ifdef CONFIG_NET_CLS_ACT
	struct tcf_proto __rcu  *ingress_cl_list;
#endif
	struct netdev_queue __rcu *ingress_queue;
#ifdef CONFIG_NETFILTER_INGRESS
	struct nf_hook_entry __rcu *nf_hooks_ingress;
#endif

	unsigned char		broadcast[MAX_ADDR_LEN];
#ifdef CONFIG_RFS_ACCEL
	struct cpu_rmap		*rx_cpu_rmap;
#endif
	struct hlist_node	index_hlist;

/*
 * Cache lines mostly used on transmit path
 */
	struct netdev_queue	*_tx ____cacheline_aligned_in_smp;
	unsigned int		num_tx_queues;
	unsigned int		real_num_tx_queues;
	struct Qdisc		*qdisc;
#ifdef CONFIG_NET_SCHED
	DECLARE_HASHTABLE	(qdisc_hash, 4);
#endif
	unsigned long		tx_queue_len;
	spinlock_t		tx_global_lock;
	int			watchdog_timeo;

#ifdef CONFIG_XPS
	struct xps_dev_maps __rcu *xps_maps;
#endif
#ifdef CONFIG_NET_CLS_ACT
	struct tcf_proto __rcu  *egress_cl_list;
#endif

	/* These may be needed for future network-power-down code. */
	struct timer_list	watchdog_timer;

	int __percpu		*pcpu_refcnt;
	struct list_head	todo_list;

	struct list_head	link_watch_list;

	enum { NETREG_UNINITIALIZED=0,
	       NETREG_REGISTERED,	/* completed register_netdevice */
	       NETREG_UNREGISTERING,	/* called unregister_netdevice */
	       NETREG_UNREGISTERED,	/* completed unregister todo */
	       NETREG_RELEASED,		/* called free_netdev */
	       NETREG_DUMMY,		/* dummy device for NAPI poll */
	} reg_state:8;

	bool dismantle;

	enum {
		RTNL_LINK_INITIALIZED,
		RTNL_LINK_INITIALIZING,
	} rtnl_link_state:16;

	void (*destructor)(struct net_device *dev);

#ifdef CONFIG_NETPOLL
	struct netpoll_info __rcu	*npinfo;
#endif

	possible_net_t			nd_net;

	/* mid-layer private */
	union {
		void					*ml_priv;
		struct pcpu_lstats __percpu		*lstats;
		struct pcpu_sw_netstats __percpu	*tstats;
		struct pcpu_dstats __percpu		*dstats;
		struct pcpu_vstats __percpu		*vstats;
	};

	//TODO UNCOMMENT struct device dev;
	const struct attribute_group *sysfs_groups[4];
	const struct attribute_group *sysfs_rx_queue_group;

	const struct rtnl_link_ops *rtnl_link_ops;

	/* for setting kernel sock attribute on TCP connection setup */
#define GSO_MAX_SIZE		65536
	unsigned int		gso_max_size;
#define GSO_MAX_SEGS		65535
	__u16			gso_max_segs;

#ifdef CONFIG_DCB
	const struct dcbnl_rtnl_ops *dcbnl_ops;
#endif
	__u8			num_tc;
	struct netdev_tc_txq	tc_to_txq[TC_MAX_QUEUE];
	__u8			prio_tc_map[TC_BITMASK + 1];

	unsigned int		fcoe_ddp_xid;
	struct netprio_map __rcu *priomap;//mby dont need?
	struct phy_device	*phydev;
	struct lock_class_key	*qdisc_tx_busylock;
	struct lock_class_key	*qdisc_running_key;
	bool			proto_down;
};
