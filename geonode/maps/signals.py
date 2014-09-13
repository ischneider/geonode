from django.dispatch import Signal

map_changed_signal = Signal(providing_args=['what_changed'])
map_copied_signal = Signal(providing_args=['source_id'])
