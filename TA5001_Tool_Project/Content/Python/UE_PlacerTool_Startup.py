import unreal

menu_owner = "New Menu"
tool_menus = unreal.ToolMenus.get()

@unreal.uclass()
class MyScriptObject(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context):
        print("SCRIPT EXECUTED")
        menuList = set()
        for i in range(1000):
            obj = unreal.find_object(None, "/Engine/Transient.ToolMenus_0:RegisteredMenu_%s" % i)
            if not obj:
                obj = unreal.find_object(None, f"/Engine/Transient.ToolsMenus_0:ToolMenu_{i}") # for legacy support
                if not obj:
                    continue
            menuName = str(obj.menu_name)
            if menuName == "None":
                continue

            menuList.add(menuName)
            print(menuName)


def create_main_menu_section():
    # Get a reference to the main menu bar
    main_menu = tool_menus.extend_menu("LevelEditor.MainMenu")

    # Add a top-level submenu
    main_menu.add_sub_menu(
        owner = menu_owner,                # owner name
        section_name = "",                # section
        name = "PythonTools",             # name of the submenu
        label = "Python Tools",            # label
        tool_tip = "Custom Python Tool Scripts"  # tooltip
    )

    # Get the submenu we just made so we can add entries to it
    python_tools_menu = tool_menus.find_menu("LevelEditor.MainMenu.PythonTools")

    # Add a section to it
    python_tools_menu.add_section("Tools", "Tools")

    # Add the entry for your Asset Placer Tool
    entry = unreal.ToolMenuEntryExtensions.init_menu_entry(
        owner=menu_owner,
        name="AssetPlacerToolEntry",
        label="Asset Placer Tool",
        tool_tip="Launch the Asset Placer Tool",
        command_type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_command_type="",
        command_string="from UE_PlacerTool import launchWindow; launchWindow()"  # command to run
    )

    # Add the entry to the section
    python_tools_menu.add_menu_entry("Tools", entry)

def run():
    # Unregister previous menus to avoid duplicates
    tool_menus.unregister_owner_by_name(menu_owner)

    create_main_menu_section()

    # Refresh the UI
    tool_menus.refresh_all_widgets()

run()