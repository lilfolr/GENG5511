/* interface.i */
%module iptables_sim
%{
/* Put header files here or function declarations like below */
typedef struct in_packets{
    int ttl;
	int protocol;
	char* src_addr;
	char* dst_addr;
	int src_port;
    int dst_port;
	char* indev;
	char* outdev;
} in_packet;

// Input struct for defining our rule
typedef struct in_rules{
	int protocol;
	char* src_addr;
	char* dst_addr;
	int src_port;
    int dst_port;
	char* indev;
	char* outdev;
} in_rule;
extern int run_sim(in_packet *packet, in_rule *rule, int debug);
%}
typedef struct in_packets{
    int ttl;
	int protocol;
	char* src_addr;
	char* dst_addr;
	int src_port;
    int dst_port;
	char* indev;
	char* outdev;
} in_packet;

typedef struct in_rules{
	int protocol;
	char* src_addr;
	char* dst_addr;
	int src_port;
    int dst_port;
	char* indev;
	char* outdev;
} in_rule;

extern int run_sim(in_packet *packet, in_rule *rule, int debug);