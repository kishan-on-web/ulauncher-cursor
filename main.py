import os
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item import ExtensionResultItem
from ulauncher.api.shared.action import RunScriptAction
from fuzzywuzzy import fuzz
 
 
class CursorExtension(Extension):
 
    def __init__(self):
        super(CursorExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
 
 
class KeywordQueryEventListener(EventListener):
 
    def on_event(self, event, extension):
        # Get the keyword and query
        keyword = event.get_keyword() == extension.preferences['cur_kw']
        query = event.get_argument() or ""
 
        # Get preferences
        home_input = extension.preferences.get('home_input', '')
        show_hidden = extension.preferences.get('show_hidden', 'False') == 'True'
        base_path = home_input.strip() or os.path.expanduser('~')
 
        # Ensure the base path exists
        if not os.path.isdir(base_path):
            return [ExtensionResultItem(
                icon='images/icon.png',
                name='Base directory not found',
                description=base_path,
                on_enter=None
            )]
 
        # List folders from base_path
        try:
            folders = []
            for entry in os.listdir(base_path):
                full_path = os.path.join(base_path, entry)
                if os.path.isdir(full_path):
                    if not show_hidden and entry.startswith('.'):
                        continue
                    folders.append(entry)
        except Exception as e:
            return [ExtensionResultItem(
                icon='images/icon.png',
                name='Error reading directory',
                description=str(e),
                on_enter=None
            )]
 
        # Fuzzy match folders
        matches = sorted(folders, key=lambda f: fuzz.partial_ratio(query.lower(), f.lower()), reverse=True)
 
        items = []
        for folder in matches[:10]:
            full_path = os.path.join(base_path, folder)
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=folder,
                description=f'Open "{folder}" in Cursor AI',
                on_enter=RunScriptAction(['cursor', full_path])
            ))
 
        if not items:
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='No matching folder found',
                description='Try a different search term',
                on_enter=None
            ))
 
        return items
 
 
class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        # No additional handling required
        return None
 
 
if __name__ == '__main__':
    CursorExtension().run()
