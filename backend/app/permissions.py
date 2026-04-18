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
    MANAGE_MENU = "manage_menu_item"
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
    UPDATE_ORDER_STATUS = "update_order_status"
    CANCEL_ORDER = "cancel_order"
    DELETE_ORDER = "delete_order"
    VIEW_ALL_ORDERS = "view_all_orders"
    
    # Cart permissions
    VIEW_CART = "view_cart"
    ADD_TO_CART = "add_to_cart"
    UPDATE_CART = "update_cart"
    CLEAR_CART = "clear_cart"
    CHECKOUT = "checkout"
    
    # Inventory permissions
    VIEW_INVENTORY = "view_inventory"
    UPDATE_INVENTORY = "update_inventory"
    
    # Staff permissions
    VIEW_STAFF = "view_staff"
    MANAGE_STAFF = "manage_staff"
    
    # Payment permissions
    VIEW_PAYMENTS = "view_payments"
    PROCESS_PAYMENT = "process_payment"
    REFUND_PAYMENT = "refund_payment"
    
    # Kitchen permissions
    VIEW_KITCHEN = "view_kitchen"
    UPDATE_KITCHEN_STATUS = "update_kitchen_status"

    # Recommendation permissions
    VIEW_RECOMMENDATIONS = "view_recommendations"
    TRAIN_MODEL = "train_model"

ROLE_PERMISSIONS = {
    UserRole.MANAGER: [
        permission for permission in Permission
    ],
    UserRole.STAFF: [
        Permission.VIEW_MENU,
        Permission.CREATE_MENU_ITEM,
        Permission.UPDATE_MENU_ITEM,
        Permission.MANAGE_MENU,
        Permission.DELETE_MENU_ITEM,
        Permission.VIEW_TABLES,
        Permission.CREATE_TABLE,
        Permission.UPDATE_TABLE,
        Permission.DELETE_TABLE,
        Permission.UPDATE_TABLE_STATUS,
        Permission.MANAGE_TABLES,
        Permission.VIEW_ORDERS,
        Permission.CREATE_ORDER,
        Permission.UPDATE_ORDER_STATUS,
        Permission.CANCEL_ORDER,
        Permission.VIEW_CART,
        Permission.ADD_TO_CART,
        Permission.UPDATE_CART,
        Permission.CLEAR_CART,
        Permission.CHECKOUT,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_STAFF,
        Permission.VIEW_PAYMENTS,
        Permission.PROCESS_PAYMENT,
    ]
}

def has_permission(user_role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    return ROLE_PERMISSIONS.get(user_role, [])