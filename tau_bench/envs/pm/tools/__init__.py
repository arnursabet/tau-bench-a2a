# Copyright Sierra

from tau_bench.envs.pm.tools.list_tickets import ListTickets
from tau_bench.envs.pm.tools.create_ticket import CreateTicket
from tau_bench.envs.pm.tools.update_status import UpdateStatus
from tau_bench.envs.pm.tools.assign_user import AssignUser
from tau_bench.envs.pm.tools.update_priority import UpdatePriority
from tau_bench.envs.pm.tools.add_comment import AddComment
from tau_bench.envs.pm.tools.get_user_details import GetUserDetails
from tau_bench.envs.pm.tools.transfer_to_human_agents import TransferToHumanAgents
from tau_bench.envs.pm.tools.think import Think

ALL_TOOLS = [
    ListTickets,
    CreateTicket,
    UpdateStatus,
    AssignUser,
    UpdatePriority,
    AddComment,
    GetUserDetails,
    TransferToHumanAgents,
    Think,
]
