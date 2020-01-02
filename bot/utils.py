from discord import ChannelType
from discord.utils import find
import asyncio
import logging
import yaml

ROLE_SUFFIX = "_role"

class Config():
    def __init__(self):
        data ={}
        with open("config.yml", "r") as f:
            data = yaml.safe_load(f)
        self.bot = data["bot"]
        self.bot_id = self.bot["id"]
        self.bot_owner = self.bot["owner"]
        self.prefix = self.bot["prefix"]
        self.debug_mode = self.bot["debug-mode"]
        self.default_cogs = self.bot["default-cogs"]

        self.guild = data["guild"]
        self.guild_id = self.guild["id"]
        self.guild_invite = self.guild["invite"]
        self.guild_roles = self.guild["roles"]
        self.guild_channels = self.guild["channels"]

        self.permissions = data["permissions"]
        self.erole_perms = self.permissions["erole"]
        self.live_perms = self.permissions["live"]
    
    def get_permissions(self, name):
        return Permissions(name, self.permissions[name]["admin"],
                self.permissions[name]["roles"], self.permissions[name]["channels"])
    
    def edit_permission(self, permission):
        self.permissions[permission.name]["admin"] = permission.admin
        self.permissions[permission.name]["roles"] = permission.roles
        self.permissions[permission.name]["channels"] = permission.channels
        self.update()
    
    def add_role(self, role):
        self.guild_roles.append({role.name+ROLE_SUFFIX:role.id})
        self.update()
    
    def remove_role(self, role):
        for r in self.guild_roles:
            if role.id in r.values():
                self.guild_roles.remove(r)
                self.update()
    
    def edit_role(self, before, after):
        for r in self.guild_roles:
            if before.id in r.values():
                self.guild_roles.remove(r)
                self.guild_roles.append({after.name+ROLE_SUFFIX:after.id})
                self.update()
    
    def add_channel(self, channel):
        self.guild_channels.append({channel.name:channel.id})
        self.update()
    
    def remove_channel(self, channel):
        for c in self.guild_channels:
            if channel.id in c.values():
                self.guild_channels.remove(c)
                self.update()
    
    def edit_channel(self, before, after):
        for c in self.guild_channels:
            if before.id in c.values():
                self.guild_channels.remove(c)
                self.guild_channels.append({after.name:after.id})
                self.update()

    def update(self):
        config = {}
        config["bot"] = {}
        config["bot"]["id"] = self.bot_id
        config["bot"]["owner"] = self.bot_owner
        config["bot"]["prefix"] = self.prefix
        config["bot"]["debug-mode"] = self.debug_mode
        config["bot"]["default-cogs"] = self.default_cogs

        config["guild"] = {}
        config["guild"]["id"] = self.guild_id
        config["guild"]["invite"] = self.guild_invite
        config["guild"]["roles"] = self.guild_roles
        config["guild"]["channels"] = self.guild_channels

        config["permissions"] = {}
        config["permissions"]["erole"] = {
            "admin": self.get_permissions("erole").admin,
            "roles": self.__link_roles(self.erole_perms["roles"]),
            "channels": self.__link_channels(self.erole_perms["channels"])
        }
        config["permissions"]["live"] = {
            "admin": self.get_permissions("live").admin,
            "roles": self.__link_roles(self.live_perms["roles"]),
            "channels": self.__link_channels(self.live_perms["channels"])
        }
        with open("config.yml", "w") as f:
            yaml.dump(config, f, Dumper=CustomAnchor, sort_keys=False)
    
    def __link_roles(self, perm_roles):
        config_roles = []
        if perm_roles is None:
            return None
        for role in perm_roles:
            for guild_role in self.guild_roles:
                if role == guild_role:
                    config_roles.append(guild_role)
        return config_roles
    
    def __link_channels(self, perm_channels):
        config_channels = []
        if perm_channels is None:
            return None
        for channel in perm_channels:
            for guild_channel in self.guild_channels:
                if channel == guild_channel:
                    config_channels.append(guild_channel)
        return config_channels
    
class Permissions():
    def __init__(self, name, admin=True, roles=[], channels=[]):
        self.name = name
        self.admin = admin
        self.roles = roles
        self.channels = channels

    def has_role(self, ctx):
        if self.roles == []:
            return True
        for role in ctx.author.roles:
            for perm_role in self.roles:
                if role.id == next(iter(perm_role.values())):
                    return True
        return False
    
    def in_channel(self, ctx):
        if self.channels == []:
            return True
        for channel in self.channels:
            if ctx.channel.id == next(iter(channel.values())):
                return True
        return False
    
    def has_permission(self, ctx):
        if self.admin and ctx.author.guild_permissions.administrator:
            return self.in_channel(ctx)
        return self.has_role(ctx) and self.in_channel(ctx)
    
    def new_roles(self, new_roles):
        self.roles = []
        for role in new_roles:
            self.roles.append({role.name+ROLE_SUFFIX:role.id})

    def new_channels(self, new_channels):
        self.channels = []
        for channel in new_channels:
            self.channels.append({channel.name:channel.id})       

class CustomAnchor(yaml.Dumper):
    def generate_anchor(self, node):
        return node.value[0][0].value.upper().replace(" ", "-")

def generate_config(bot):
    guild = find(lambda g: g.id == 303523939337109505, bot.guilds)
    config = {}
    config["bot"] = {}
    config["bot"]["id"] = bot.user.id
    config["bot"]["owner"] = bot.owner_id
    config["bot"]["prefix"] = bot.command_prefix
    config["bot"]["debug-mode"] = False
    config["bot"]["default-cogs"] = [
            "bot.cogs.manager",
            "bot.cogs.base_commands",
            "bot.cogs.startup",
            "bot.cogs.role_manager",
            "bot.cogs.live_alerts",
            "bot.cogs.syncer",
            "bot.cogs.permissions"
    ]

    config["guild"] = {}
    config["guild"]["id"] = guild.id
    config["guild"]["invite"] = "[COMMAND] TO SET THIS"
    config["guild"]["roles"] = []
    for role in guild.roles:
        if role.name != "@everyone":
            config["guild"]["roles"].append({role.name+ROLE_SUFFIX:role.id})
    config["guild"]["channels"] = []
    for channel in guild.channels:
        if channel.type == ChannelType.text:
            config["guild"]["channels"].append({channel.name:channel.id})
    config["permissions"] = {}
    config["permissions"]["erole"] = {
        "admin": True,
        "roles": [],
        "channels": []
    }
    config["permissions"]["live"] = {
        "admin": True,
        "roles": [],
        "channels": []
    }
    with open("config.yml", "w") as f:
        yaml.dump(config, f, Dumper=CustomAnchor, sort_keys=False)







