"""
| Responses will always be in the form of an array/list.  
| The first element will be either **"S"** or **"E"** - dictating whether the function completed Successfully, or threw an Error.

"""

import logging
import socketio
import csv
from io import StringIO
from aiohttp import web
from application import *

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

active_users = {}


async def index(request):
    """Serve the client-side application."""
    with open(base_index + 'index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

# ======================== CONTROL ========================

@sio.on('connect', namespace='')
def connect(sid, environ):
    """Used to connect to the socket
    
    Args:
        sid (str):  Unique identifier for the socket connection

    The *sid* is automatically assigned, and, assuming you're using a good library, should
    be automatically sent with all future requests.
    *sid* is an arg for all requests
    """
    logger.info("{} connected ".format(sid))
    active_users[sid] = Application()

@sio.on('disconnect', namespace='')
def disconnect(sid):
    """Used to gracefully disconnect from the client"""
    logger.info('{} disconnected '.format(sid))
    active_users.pop(sid)

# ======================== NODES ========================
@sio.on('create-node', namespace='')
async def create_node(sid, data):
    """Used to create a new node on the network

    Args:
        data (str): A string with a unique node id

    Example Request:
        | ``socket.emit('create-node', <node_id>)``
        | ``socket.emit('create-node', 0)``

    Returns: 
        JSON Object: ``["S", "Node Created"]``

    Raises:
        ValueError: If node id is already taken
    """
    logger.debug("Creating node.")
    try:
        check_user(sid)
        node_id = data
        active_users[sid].create_node(node_id)
    except Exception as e:
        return ["E", "Error creating node - "+str(e)]
    else:
        return ["S", "Node Created"]

@sio.on('delete-node', namespace='')
async def delete_node(sid, data):
    """Used to delete an existing node on the network

    Args:
        data (str): A string with the node id

    Example Request:
        | ``socket.emit('delete-node', <node_id>)``
        | ``socket.emit('delete-node', 0)``

    Returns: 
        JSON Object: ``["S", "Node deleted"]``

    Raises:
        KeyError: if node id does not exist

    """
    logger.debug("Deleting node.")
    try:
        check_user(sid)
        node_id = data
        active_users[sid].destroy_node(node_id)
    except Exception as e:
        return ["E", "Error deleting node - "+str(e)]
    else:
        return ["S", "Node deleted "]

@sio.on('add-edge', namespace='')
async def connect_nodes(sid, data):
    """**DEPRECATED**"""
    try:
        check_user(sid)
        active_users[sid].connect_nodes(data[0], data[1])
    except Exception as e:
        return ["E", "Error connecting nodes - "+str(e)]
    else:
        return ["S", "Nodes connected "]

@sio.on('update-status-table', namespace='')
async def update_status_table_def(sid, data):
    """Used to get the current nodes

    Args:
        data (str): Can be either ``""`` or ``"loud"``. ``"loud"`` will cause the response to be "Table update triggered".

    Example Request:
        | ``socket.emit('update-status-table', null)``
        | ``socket.emit('update-status-table', "loud")``

    Returns: 
        JSON Object: ``["N"]`` or ``["S", "Table update triggered"]``
    
    | This function doesn't return anything, rather triggers a seperate update.
    | It will trigger the webserver.update_status_table_ function.

    """
    await update_status_table(sid)
    print(data)
    if data == "loud":
        return ["S", "Table update triggered"]
    # Quite update
    return ["N"]

# ======================== FIREWALL ========================

@sio.on('get-firewall', namespace='')
async def get_firewall(sid, node_id):
    """Returns the current firewall for a given node id

    Args:
        node_id (str): A string with the node id

    Example Request:
        | ``socket.emit('delete-node', <node_id>)``
        | ``socket.emit('get-firewall', 0)``

    Returns: 
        JSON Object: ``["S", "", <firewall_structure>]``
        The firewall structure is a list of chains, each of which contains a list of rules [under the ``children`` key]

    Example firewall_structure::
    
        {
            [  
                {  
                    "id":"INPUT",
                    "label":"INPUT",
                    "children":[  
                        {  
                            "id":0,
                            "label":"-i Any -o Any -p Any -s Any -d Any -j DROP"
                        }
                    ]
                },
                {  
                    "id":"FORWARD",
                    "label":"FORWARD",
                    "children":[  
                        {  
                            "id":0,
                            "label":"-i Any -o Any -p Any -s Any -d Any -j DROP"
                        }
                    ]
                },
                {  
                    "id":"OUTPUT",
                    "label":"OUTPUT",
                    "children":[  
                        {  
                            "id":0,
                            "label":"-i Any -o Any -p Any -s Any -d Any -j DROP"
                        }
                    ]
                },
                {  
                    "id":"ACCEPT",
                    "label":"ACCEPT",
                    "children":[  
                        {  
                            "id":0,
                            "label":"-i Any -o Any -p Any -s Any -d Any -j ACCEPT"
                        }
                    ]
                },
                {  
                    "id":"REJECT",
                    "label":"REJECT",
                    "children":[  
                        {  
                            "id":0,
                            "label":"-i Any -o Any -p Any -s Any -d Any -j REJECT"
                        }
                    ]
                },
                {  
                    "id":"DROP",
                    "label":"DROP",
                    "children":[  
                        {  
                            "id":0,
                            "label":"-i Any -o Any -p Any -s Any -d Any -j DROP"
                        }
                    ]
                }
            ]
        }

    Raises:
        KeyError: if node id does not exist

    """
    try:
        check_user(sid)
        to_return = []
        firewall = active_users[sid].get_node_firewall(node_id)
        for chain, rules in firewall.chains.items():
            chain = str(chain)
            chain = {
                "id" : chain,
                "label": chain,
                "children": []
            }
            i = 0
            for rule in rules:
                child = {
                    "id": i,
                    "label": "-i {} -o {} -p {} -s {} -d {} --sport {} --dport -j {}".format(rule.input_device, rule.output_device, 
                                                                          rule.protocol, rule.src, rule.dst, rule.src_port, rule.dst_port, rule.match_chain).replace("None", "Any")
                }
                chain["children"].append(child)
                i += 1
            to_return.append(chain)
        return ["S", "", to_return]
    except Exception as e:
        return ["E", "Error getting firewall - "+str(e)]

@sio.on('delete-rule')
def delete_rule(sid, data):
    """Delete a set of rules from a node's firewall
    
    Args: 
        data (JSON)::

            {
                [node_id,
                    [
                        [chain1_id, rule1_id],
                        [chain2_id, rule2_id],
                        ...
                    ]
                ]
            }

    Example Request data::

        {
            [0,
                [
                    ["INPUT",0]
                ]
            ]
        }

    Returns:
        JSON Object: ``["S", "Rules deleted"]``

    """
    try:
        check_user(sid)
        node_id = data[0]
        rules = data[1]
        for r in rules:
            chain, rule = r
            logger.info("Deleting {} from {} - node {}".format(rule, chain, node_id))
            active_users[sid].get_node_firewall(node_id).remove_chain_rule(chain, rule)
        return ["S", "Rules deleted"]
    except Exception as e:
        return ["E", "Error deleting rules - "+str(e)]

async def update_status_table(sid):
    """ Send a status update for all nodes


    Returns:
        List of nodes, with their properties

    Example Response::

        {
            [
                {
                    "Node_ID":0,
                    "Node_Addr":"10.62.0.0",
                    "Node_Mac":"62:f4:e5:9c:00:00",
                    "Packets_In":"",
                    "Packets_Out":""
                },
                {
                    "Node_ID":1,
                    "Node_Addr":"10.51.0.1",
                    "Node_Mac":"1e:68:26:a7:00:01",
                    "Packets_In":"",
                    "Packets_Out":""
                }
            ]
        }
    
    Note:
        | ``Packets_In`` and ``Packets_Out`` will be blank when running this function.
        | The fields are populated after the simulation runs.
    """

    toreturn = []
    for node_id, node_data in active_users[sid].current_nodes.items():
        toreturn.append({
            "Node_ID": node_id,
            "Node_Addr": node_data['ip'],
            "Node_Mac": node_data['mac'],
            "Packets_In": '',
            "Packets_Out": '',
        })
    await sio.emit('update-table', data=toreturn, room=sid)

@sio.on('add-rule')
def add_rule(sid, data):
    """Adds rule to a node's firewall.

    Args:
        data (JSON): ``[node_id, chain_id, <rule_object>]``

    Example Request::

        {
            [  
                0,
                "INPUT",
                {  
                    "chain":"New_Chain",
                    "dst":false,
                    "src":"",
                    "input_device":"",
                    "output_device":false,
                    "protocol":false
                }
            ]
        }

    Returns: 
        ``["S","Rule added."]`` or ``["S","Rule added. New chain New_Chain created"]``

    | In the above, "INPUT" is the chain the rule is appended to, and "New_Chain" is the name of the chain the rule processor goes to if the rule matches the given packet.
    | Note that "New_Chain" can be either a new chain, an existing chain, or a final status ["ACCEPT"; "DROP"; "REJECT"]
    """
    import iptables_sim_interface as ip
    try:
        msg = "Rule added"
        check_user(sid)
        node_id = data[0]
        chain = data[1]
        rule = data[2]
        logger.info("Adding {} from {} - node {}".format(rule, chain, node_id))
        firewall = active_users[sid].get_node_firewall(node_id)
        ip_rule = ip.Rule()
        ip_rule.input_device = rule["input_device"] if rule["input_device"] else None
        ip_rule.output_device = rule["output_device"] if rule["output_device"] else None
        ip_rule.protocol = rule["protocol"] if rule["protocol"] else None
        ip_rule.src = rule["src"] if rule["src"] else None
        ip_rule.dst = rule["dst"] if rule["dst"] else None
        ip_rule.src_port = rule['src_port'] if rule["src_port"] else None
        ip_rule.dst_port = rule['dst_port'] if rule["dst_port"] else None
        if not rule["chain"]:
            raise ValueError("Match chain must have a value")
        if rule["chain"] not in firewall.chains.keys():
            firewall.create_chain(rule["chain"])
            msg += ". New chain {} created".format(rule["chain"])
        ip_rule.match_chain = rule["chain"]
        firewall.add_chain_rule(chain, ip_rule, 0)  #TODO: allow custom index location
        return ["S", msg]
    except Exception as e:
        return ["E", "Error adding rule - "+str(e)]

# ======================== SIMULATION ========================

@sio.on('download-sim-template', namespace='')
async def download_sim_file(sid, data):
    """ Used to download a simulation template, in csv format

        Args:
            data (str): Just leave empty

        Returns:
            Simulation template ``["S", "", <template>]``

        Example Response template:
            ``"packet_id,network_layer,source_port,destination_port,source_ip,destination_ip,input_device,output_device,ttl \\r\\n 1,icmp,,,,10.47.0.0,,eth1,eth1,2 \\r\\n"``

    """
    try:
        check_user(sid)
        str_template = active_users[sid].get_sim_template()
        return ["S","", str_template]
    except Exception as e:
        return ["E", "Error generating tempalte - "+str(e)]

@sio.on('upload-sim', namespace='')
async def upload_simulation_file(sid, data):
    """Upload the packets to be simulated. This should be called before running the simulation.

       Args:
           data: (str): The simulation file [csv format]

       Example Request data::
          ``"packet_id,network_layer,application_layer,source_port,destination_port,source_ip,destination_ip,input_device,output_device,ttl\\r\\n1,icmp,,,,10.47.0.0,10.48.0.0,eth1,eth1,2"``
        

       Returns:
           ``["S","Simulation file uploaded"]``

       Raises:
           If a row is invalid you will get an error stating which row failed

       Note:
           The first row is ignored [as it contains column titles]
    """
    try:
        check_user(sid)
        file_data = StringIO(data)  #WARNING: could contain malicious things
        reader = csv.reader(file_data, delimiter=',')
        active_users[sid].set_sim_packets(reader)
        return ["S","Simulation file uploaded"]
        
    except Exception as e:
        return ["E", "Error uploading simulation - "+str(e)]

@sio.on('run-simulation', namespace='')
async def run_simulation(sid, data):
    """Runs the simulation on the created nodes with the uploaded packets.

       Args:
           data (str): Leave empty

       Returns:
           ``["S","Simulation 2 Complete"]``


       Note:
           | Packets **must** have been set from the webserver.upload_simulation_file_ method.
           | Results can be retrieved from the webserver.get_sim_results_ method
    """
    try:
        check_user(sid)

        results_out = {q:[0, 0, 0] for q in active_users[sid].current_nodes.keys()}   # node: (total, blocked)
        results_in =  {q:[0, 0, 0] for q in active_users[sid].current_nodes.keys()}   # node: (total, blocked)
        for packet_result in active_users[sid].simulate():
            results_out[packet_result[0][0]][0] += packet_result[0][1][0]
            results_out[packet_result[0][0]][1] += packet_result[0][1][1]
            results_out[packet_result[0][0]][2] += packet_result[0][1][2]
            results_in[packet_result[1][0]][0] += packet_result[1][1][0]
            results_in[packet_result[1][0]][1] += packet_result[1][1][1]
            results_in[packet_result[1][0]][2] += packet_result[1][1][2]
        update_table=[]
        for node_id, node_data in active_users[sid].current_nodes.items():
            update_table.append({
                "Node_ID": node_id,
                "Node_Addr": node_data['ip'],
                "Node_Mac": node_data['mac'],
                "Packets_In": "{} | {} | {}".format(*results_in[node_id]),
                "Packets_Out": "{} | {} | {}".format(*results_out[node_id])
            })
        await sio.emit('update-table', data=update_table, room=sid)
            
        return ["S","Simulation {:d} Complete".format(active_users[sid].simulation_run_number)]
    except Exception as e:
        raise
        return ["E", "Error running simulation - "+str(e)]

@sio.on('get-sim-results', namespace='')
async def get_sim_results(sid,data):
    """Returns the simulation results after running.
       Results are in 3 parts: packet results; node results and rule results

       * Packet results: 1 row per packet, stating what happened to it [dropped; accepted...]
       * Node results: 1 row per node per packet. States what happened to a packet at each node it reached
       * Rule results: 1 row per rule per packet. States what happened to a packet at each rule in each node it hit
          
       Args:
           data (str): Leave empty

       Returns:
           ``["S","", <results>]``


       Example results::

            {
                "packet":"Simulation_Run_Number,Packet_ID,Source_IP,Destination_IP,Protocol,Result\\r\\n-1,10.87.0.0,10.198.0.1,ICMP,DROP\\r\\n-1,10.198.0.1,10.87.0.0,ICMP,DROP\\r\\n",
                "node":"Simulation_Run_Number,Packet_ID,Hop_Number,Node_IP,Direction,Protocol,Result\\r\\n-1,1,10.87.0.0,Output,ICMP,DROP\\r\\n-1,1,10.198.0.1,Output,ICMP,DROP\\r\\n",
                "rule":"Simulation_Run_Number,Packet_ID,Node_IP,Chain,Protocol,Rule,Result\\r\\n-1,10.87.0.0,OUTPUT,ICMP,P:ICMP S: D: iD: oD:,DROP\\r\\n-1,10.198.0.1,OUTPUT,ICMP,P:ICMP S: D: iD: oD:,DROP\\r\\n"
            }

       Note:
          This must only be called **after** running the simulation - see webserver.run_simulation_
    """
    try:
        print("AA")
        check_user(sid)
        to_return = {"packet":"","node":"","rule":""}
        # Packet
        file_data = StringIO() 
        writer = csv.DictWriter(file_data, ['Simulation_Run_Number', 'Packet_ID', 'Source_IP', 'Destination_IP', 'Protocol', 'Result'])
        writer.writeheader()
        writer.writerows(active_users[sid].sim_results['packet_results'])
        print("here")
        to_return["packet"] = file_data.getvalue()
        # Node
        file_data = StringIO() 
        writer = csv.DictWriter(file_data, ['Simulation_Run_Number', 'Packet_ID', 'Hop_Number', 'Node_IP', 'Direction', 'Protocol', 'Result' ])
        writer.writeheader()
        writer.writerows(active_users[sid].sim_results["node_results"])
        print("here2")
        to_return["node"] = file_data.getvalue()
        # Rule
        file_data = StringIO() 
        writer = csv.DictWriter(file_data, ['Simulation_Run_Number', 'Packet_ID', 'Node_IP', 'Chain', 'Protocol', 'Rule', 'Result'])
        writer.writeheader()
        writer.writerows(active_users[sid].sim_results["rule_results"])
        to_return["rule"] = file_data.getvalue()
        print("to_return - {}".format(to_return))
        return ["S","", to_return]
    except Exception as e:
        return ["E", "Error uploading simulation - "+str(e)]

def check_user(sid):
    if sid not in active_users:
        raise Exception("User not active")

app.router.add_static('/css', base_index + 'css')
app.router.add_static('/js', base_index + 'js')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)
