"""Provide the Redditor class."""
from json import dumps

from .mixins import (GildableMixin, InboxableMixin, MessageableMixin,
                     RedditorListingMixin)
from ..const import API_PATHS
from ..errors import ClientException


class Redditor(GildableMixin, MessageableMixin, RedditorListingMixin):
    """A class representing the users of reddit."""

    _methods = (('get_multireddit', 'MultiMix'),
                ('get_multireddits', 'MultiMix'))

    def __init__(self, reddit, name=None, json_dict=None, fetch=False,
                 **kwargs):
        """Construct an instance of the Redditor object."""
        if not name:
            name = json_dict['name']

        info_path = API_PATHS['user_about'].format(user=name)
        super(Redditor, self).__init__(reddit, json_dict, fetch, info_path,
                                       **kwargs)
        if 'name' not in self.__dict__:
            self.name = name
        self._path = API_PATHS['user'].format(user=self.name)
        self._listing_use_sort = True

    def __repr__(self):
        """Return a code representation of the Redditor."""
        return 'Redditor(user_name=\'{0}\')'.format(self.name)

    def __unicode__(self):
        """Return a string representation of the Redditor."""
        return self.name

    def friend(self, note=None, _unfriend=False):
        """Friend the user.

        :param note: A personal note about the user. Requires reddit Gold.
        :param _unfriend: Unfriend the user. Please use :meth:`unfriend`
            instead of setting this parameter manually.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        # This endpoint wants the data to be a string instead of an actual
        # dictionary, although it is not required to have any content for adds.
        # Unfriending does require the 'id' key.
        if _unfriend:
            data = {'id': self.name}
        else:
            # We cannot send a null or empty note string.
            data = {'note': note} if note else {}
        method = 'DELETE' if _unfriend else 'PUT'
        return self.reddit_session.request_json(url, data=dumps(data),
                                                method=method)

    def get_blocked(self):
        """Return a UserList of Redditors with whom the user has blocked."""
        url = self.reddit_session.config['blocked']
        return self.reddit_session.request_json(url)

    def get_friend_info(self):
        """Return information about this friend, including personal notes.

        The personal note can be added or overwritten with :meth:friend, but
            only if the user has reddit Gold.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        data = {'id': self.name}
        return self.reddit_session.request_json(url, data=data, method='GET')

    def mark_as_read(self, messages, unread=False):
        """Mark message(s) as read or unread.

        :returns: The json response from the server.

        """
        ids = []
        if isinstance(messages, InboxableMixin):
            ids.append(messages.fullname)
        elif hasattr(messages, '__iter__'):
            for message in messages:
                if not isinstance(message, InboxableMixin):
                    raise ClientException('Invalid message type: {0}'
                                          .format(type(message)))
                ids.append(message.fullname)
        else:
            raise ClientException('Invalid message type: {0}'
                                  .format(type(messages)))
        retval = self.reddit_session._mark_as_read(ids, unread=unread)
        return retval

    def unfriend(self):
        """Unfriend the user.

        :returns: The json response from the server.

        """
        return self.friend(_unfriend=True)