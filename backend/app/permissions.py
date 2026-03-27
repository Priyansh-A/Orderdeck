from enum import Enum
from typing import List

class UserRole(str, Enum):
    MANAGER = "manager"
    STAFF = "staff"

class Permission(str, Enum):
    # Menu permissions
    VIEW_MENU = "view_menu"
    CREATE_MENU_ITEM = "create_menu_item"
    UPDATE_MENU_ITEM = "update_menu_item"
    DELETE_MENU_ITEM = "delete_menu_item"
    
    # Table permissions
    VIEW_TABLES = "view_tables"
    CREATE_TABLE = "create_table"
    UPDATE_TABLE = "update_table"
    DELETE_TABLE = "delete_table"
    UPDATE_TABLE_STATUS = "update_table_status"
    MANAGE_TABLES = "manage_tables"
    
    # Order permissions
    VIEW_ORDERS = "view_orders"
    CREATE_ORDER = "create_order"
    UPDATE_ORDER = "update_order"
    CANCEL_ORDER = "cancel_order"
    
    # Inventory permissions
    VIEW_INVENTORY = "view_inventory"
    UPDATE_INVENTORY = "update_inventory"
    
    # Staff permissions
    VIEW_STAFF = "view_staff"
    MANAGE_STAFF = "manage_staff"
    
    # Financial permissions
    VIEW_SALES = "view_sales"
    PROCESS_PAYMENT = "process_payment"
    VIEW_REPORTS = "view_reports"
    

ROLE_PERMISSIONS = {
    UserRole.MANAGER: [
    permission for permission in Permission
    ],
    UserRole.STAFF: [
        Permission.VIEW_MENU, Permission.CREATE_MENU_ITEM, Permission.UPDATE_MENU_ITEM, Permission.DELETE_MENU_ITEM,
        Permission.VIEW_ORDERS, Permission.CREATE_ORDER, Permission.UPDATE_ORDER, Permission.CANCEL_ORDER,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_STAFF,
        Permission.VIEW_SALES, Permission.PROCESS_PAYMENT,
        Permission.CREATE_TABLE, Permission.VIEW_TABLES,Permission.DELETE_TABLE, Permission.UPDATE_TABLE, Permission.UPDATE_TABLE_STATUS
    ]
}

def has_permission(user_role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    return ROLE_PERMISSIONS.get(user_role, [])

# Helper decorator for routes
def requires_permissions(permissions: List[Permission]):
    def decorator(func):
        return func
    return decorator