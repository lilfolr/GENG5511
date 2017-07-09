/* interface.i */
%module iptables_sim
%{
/* Put header files here or function declarations like below */
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
extern int run_sim(in_packet *packet, in_rule *rule);
%}
typedef struct in_packets{
    int ttl;
	int protocol;
	char* dst_addr;
	char* src_addr;
} in_packet;

typedef struct in_rules{
	int protocol;
	char* src_addr;
	char* dst_addr;
	char* indev;
	char* outdev;
} in_rule;

extern int run_sim(in_packet *packet, in_rule *rule);
