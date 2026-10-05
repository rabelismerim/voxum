import time

from channels_redis.core import RedisChannelLayer


class ExtendedRedisChannelLayer(RedisChannelLayer):

    async def get_group_channels(self, group):
        if not self.valid_group_name(group):
            raise ValueError(f"Group name '{group}' is not valid")

        key = self._group_key(group)
        connection = self.connection(self.consistent_hash(group))
        # Discard old channels based on group_expiry
        await connection.zremrangebyscore(
            key, min=0, max=int(time.time()) - self.group_expiry
        )

        return [x.decode("utf8") for x in await connection.zrange(key, 0, -1)]

    async def count_group_connections(self, group):
        if not self.valid_group_name(group):
            raise ValueError(f"Group name '{group}' is not valid")

        key = self._group_key(group)
        connection = self.connection(self.consistent_hash(group))
        return await connection.zcard(key)