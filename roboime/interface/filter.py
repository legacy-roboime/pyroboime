from math import degrees


class Filter(object):
    """The filter class is the base for all filters.

    Filters should basically contain an filter_updates and
    filter_commands methods, those will be called with an
    iterator of updates and a list of commands respectively.

    Neither of those methods need to be implemented and
    if they return None the flow will continue.

    However if they return anything other than None it
    will replace the updates or commands for the next call.

    Please avoid returning lists, an iterator will generally
    have better perfomance and memory usage.
    """

    def filter_updates(self, updates):
        pass

    def filter_commands(self, commands):
        pass


class Scale(Filter):

    def filter_updates(self, updates):
        for update in updates:
            filtered_data = {}
            for key, value in update.data.iteritems():
                if key == 'timestamp':
                    filtered_data[key] = value
                elif key == 'angle':
                    filtered_data[key] = degrees(value)
                else:
                    filtered_data[key] = value / 1000.0
            update.data = filtered_data
