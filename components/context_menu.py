from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QIcon
import components.folders as folders  # Importing the module for folder management

def create_context_menu(parent, position, new_note_callback, new_folder_callback, refresh_callback, rename_callback, trash_callback, complete_callback, move_callback):
    menu = QMenu(parent)
    menu.setStyleSheet("""
        QMenu {
            background-color: #fff; /* Menu background color */
            color: #000; /* Menu text color */
            border: 1px solid #aaa; /* Menu border color */
            border-radius: 8px; /* Menu corner radius */
        }
        QMenu::item {
            background-color: transparent;
            padding: 10px 10px;
            color: #000;  /* Menu item text color */
        }
        QMenu::item:selected {
            background-color: #0078d4; /* Background color when item is hovered */
            color: #fff; /* Text color when item is hovered */
            border-radius: 8px; /* Menu item corner radius */
        }
        QMenu::icon:selected {
            background-color: transparent;
        }
        QMenu::icon {
            padding: 5px;
        }
    """)

    # New Note and New Folder actions
    new_note_action = QAction(QIcon("icons/new_note_icon.png"), "New Note", parent)
    new_folder_action = QAction(QIcon("icons/new_folder_icon.png"), "New Folder", parent)
    refresh_action = QAction(QIcon("icons/refresh_icon.png"), "Refresh", parent)

    menu.addAction(new_note_action)
    menu.addAction(new_folder_action)
    menu.addAction(refresh_action)

    # Rename, Move to Trash, Complete, and Move actions
    rename_action = QAction(QIcon("icons/rename_icon.png"), "Rename", parent)
    trash_action = QAction(QIcon("icons/trash_icon.png"), "Move to Recycle Bin", parent)
    complete_action = QAction(QIcon("icons/complete_icon.png"), "Complete", parent)

    move_menu = QMenu("Move", parent)  # Move menu
    move_menu.setStyleSheet("""
        QMenu {
            background-color: #fff; /* Menu background color */
            color: #000; /* Menu text color */
            border: 1px solid #333; /* Menu border color */
            border-radius: 8px; /* Menu corner radius */
        }
        QMenu::item {
            background-color: transparent;
            padding: 10px 10px;
            color: #000;  /* Menu item text color */
        }
        QMenu::item:selected {
            background-color: #0078d4; /* Background color when item is hovered */
            color: #fff; /* Text color when item is hovered */
            border-radius: 8px; /* Menu item corner radius */
        }
        QMenu::icon:selected {
            background-color: transparent;
        }
        QMenu::icon {
            padding: 5px;
        }
    """)
    move_action = QAction(QIcon("icons/move_icon.png"), "Move", parent)  # Add icon for Move action

    # Add Move Back action first
    move_menu.addAction(QAction(QIcon("icons/move_icon.png"), "Move Back", parent, triggered=lambda: move_callback(0)))

    # Add folder actions
    folders_list = folders.get_folders()
    for folder in folders_list:
        folder_action = QAction(QIcon("icons/folder_icon.png"), folder[1], parent)
        folder_action.triggered.connect(lambda checked, folder_id=folder[0]: move_callback(folder_id))
        move_menu.addAction(folder_action)

    move_action.setMenu(move_menu)
    
    menu.addAction(rename_action)
    menu.addAction(trash_action)
    menu.addAction(complete_action)
    menu.addAction(move_action)

    action = menu.exec_(parent.note_list.viewport().mapToGlobal(position))
    item = parent.note_list.itemAt(position)

    if action == new_note_action:
        new_note_callback()
    elif action == new_folder_action:
        new_folder_callback()
    elif action == refresh_action:
        refresh_callback()
    elif item is not None:
        if action == rename_action:
            rename_callback(item)
        elif action == trash_action:
            trash_callback(item)
        elif action == complete_action:
            complete_callback(item)
