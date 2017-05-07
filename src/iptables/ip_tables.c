/*
 * Packet matching code.
 *
 * Copyright (C) 1999 Paul `Rusty' Russell & Michael J. Neuling
 * Copyright (C) 2000-2005 Netfilter Core Team <coreteam@netfilter.org>
 * Copyright (C) 2006-2010 Patrick McHardy <kaber@trash.net>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <stdbool.h>
#include <stddef.h>
#include <netdb.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include "ip_tables.h"

static inline bool
ip_packet_match(const struct iphdr *ip,
		const char *indev,
		const char *outdev,
		const struct ipt_ip *ipinfo,
		int isfrag)
{
	unsigned long ret;

	if (NF_INVF(ipinfo, IPT_INV_SRCIP,
		    (ip->saddr & ipinfo->smsk.s_addr) != ipinfo->src.s_addr) ||
	    NF_INVF(ipinfo, IPT_INV_DSTIP,
		    (ip->daddr & ipinfo->dmsk.s_addr) != ipinfo->dst.s_addr))
		return false;

	ret = ifname_compare_aligned(indev, ipinfo->iniface, ipinfo->iniface_mask);

	if (NF_INVF(ipinfo, IPT_INV_VIA_IN, ret != 0))
		return false;

	ret = ifname_compare_aligned(outdev, ipinfo->outiface, ipinfo->outiface_mask);

	if (NF_INVF(ipinfo, IPT_INV_VIA_OUT, ret != 0))
		return false;

	/* Check specific protocol */
	if (ipinfo->proto &&
	    NF_INVF(ipinfo, IPT_INV_PROTO, ip->protocol != ipinfo->proto))
		return false;

	/* If we have a fragment rule but the packet is not a fragment
	 * then we return zero */
	if (NF_INVF(ipinfo, IPT_INV_FRAG,
		    (ipinfo->flags & IPT_F_FRAG) && !isfrag))
		return false;

	return true;
}


/* Performance critical */
static inline struct ipt_entry *
get_entry(const void *base, unsigned int offset)
{
	return (struct ipt_entry *)(base + offset);
}

/* All zeroes == unconditional rule. */
/* Mildly perf critical (only if packet tracing is on) */
static inline bool unconditional(const struct ipt_entry *e)
{
	static const struct ipt_ip uncond;

	return e->target_offset == sizeof(struct ipt_entry) &&
	       memcmp(&e->ip, &uncond, sizeof(uncond)) == 0;
}

/* for const-correctness */
static inline const struct xt_entry_target *
ipt_get_target_c(const struct ipt_entry *e)
{
	return ipt_get_target((struct ipt_entry *)e);
}


static inline
struct ipt_entry *ipt_next_entry(const struct ipt_entry *entry)
{
	return (void *)entry + entry->next_offset;
}


/* Returns one of the generic firewall policies, like NF_ACCEPT. */

// unsigned int
// ipt_do_table(struct sk_buff *skb,
// 	     const struct nf_hook_state *state,
// 	     struct xt_table *table)
// {
// 	unsigned int hook = state->hook;
// 	static const char nulldevname[IFNAMSIZ] __attribute__((aligned(sizeof(long))));
// 	const struct iphdr *ip;
// 	/* Initializing verdict to NF_DROP keeps gcc happy. */
// 	unsigned int verdict = NF_DROP;
// 	const char *indev, *outdev;
// 	const void *table_base;
// 	struct ipt_entry *e, **jumpstack;
// 	unsigned int stackidx, cpu;
// 	const struct xt_table_info *private;
// 	struct xt_action_param acpar;
// 	unsigned int addend;

// 	/* Initialization */
// 	stackidx = 0;
// 	ip = ip_hdr(skb);
// 	indev = state->in ? state->in->name : nulldevname;
// 	outdev = state->out ? state->out->name : nulldevname;
// 	/* We handle fragments by dealing with the first fragment as
// 	 * if it was a normal packet.  All other fragments are treated
// 	 * normally, except that they will NEVER match rules that ask
// 	 * things we don't know, ie. tcp syn flag or ports).  If the
// 	 * rule is also a fragment-specific rule, non-fragments won't
// 	 * match it. */
// 	acpar.fragoff = ntohs(ip->frag_off) & IP_OFFSET;
// 	acpar.thoff   = ip_hdrlen(skb);
// 	acpar.hotdrop = false;
// 	acpar.state   = state;

// 	IP_NF_ASSERT(table->valid_hooks & (1 << hook));
// 	local_bh_disable();
// 	addend = xt_write_recseq_begin();
// 	private = table->private;
// 	cpu        = smp_processor_id();
// 	/*
// 	 * Ensure we load private-> members after we've fetched the base
// 	 * pointer.
// 	 */
// 	smp_read_barrier_depends();
// 	table_base = private->entries;
// 	jumpstack  = (struct ipt_entry **)private->jumpstack[cpu];

// 	/* Switch to alternate jumpstack if we're being invoked via TEE.
// 	 * TEE issues XT_CONTINUE verdict on original skb so we must not
// 	 * clobber the jumpstack.
// 	 *
// 	 * For recursion via REJECT or SYNPROXY the stack will be clobbered
// 	 * but it is no problem since absolute verdict is issued by these.
// 	 */
// 	if (static_key_false(&xt_tee_enabled))
// 		jumpstack += private->stacksize * __this_cpu_read(nf_skb_duplicated);

// 	e = get_entry(table_base, private->hook_entry[hook]);

// 	do {
// 		const struct xt_entry_target *t;
// 		const struct xt_entry_match *ematch;
// 		struct xt_counters *counter;

// 		IP_NF_ASSERT(e);
// 		if (!ip_packet_match(ip, indev, outdev,
// 		    &e->ip, acpar.fragoff)) {
//  no_match:
// 			e = ipt_next_entry(e);
// 			continue;
// 		}

// 		xt_ematch_foreach(ematch, e) {
// 			acpar.match     = ematch->u.kernel.match;
// 			acpar.matchinfo = ematch->data;
// 			if (!acpar.match->match(skb, &acpar))
// 				goto no_match;
// 		}

// 		counter = xt_get_this_cpu_counter(&e->counters);
// 		ADD_COUNTER(*counter, skb->len, 1);

// 		t = ipt_get_target(e);
// 		IP_NF_ASSERT(t->u.kernel.target);

// #if IS_ENABLED(CONFIG_NETFILTER_XT_TARGET_TRACE)
// 		/* The packet is traced: log it */
// 		if (skb->nf_trace)
// 			trace_packet(state->net, skb, hook, state->in,
// 				     state->out, table->name, private, e);
// #endif
// 		/* Standard target? */
// 		if (!t->u.kernel.target->target) {
// 			int v;

// 			v = ((struct xt_standard_target *)t)->verdict;
// 			if (v < 0) {
// 				/* Pop from stack? */
// 				if (v != XT_RETURN) {
// 					verdict = (unsigned int)(-v) - 1;
// 					break;
// 				}
// 				if (stackidx == 0) {
// 					e = get_entry(table_base,
// 					    private->underflow[hook]);
// 				} else {
// 					e = jumpstack[--stackidx];
// 					e = ipt_next_entry(e);
// 				}
// 				continue;
// 			}
// 			if (table_base + v != ipt_next_entry(e) &&
// 			    !(e->ip.flags & IPT_F_GOTO))
// 				jumpstack[stackidx++] = e;

// 			e = get_entry(table_base, v);
// 			continue;
// 		}

// 		acpar.target   = t->u.kernel.target;
// 		acpar.targinfo = t->data;

// 		verdict = t->u.kernel.target->target(skb, &acpar);
// 		/* Target might have changed stuff. */
// 		ip = ip_hdr(skb);
// 		if (verdict == XT_CONTINUE)
// 			e = ipt_next_entry(e);
// 		else
// 			/* Verdict */
// 			break;
// 	} while (!acpar.hotdrop);

// 	xt_write_recseq_end(addend);
// 	local_bh_enable();

// 	if (acpar.hotdrop)
// 		return NF_DROP;
// 	else return verdict;
// }
