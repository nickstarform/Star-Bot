package io.ph.bot.commands.owner;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.jobs.StatusChangeJob;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import io.ph.bot.Bot;

import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.EmbedBuilder;

import java.awt.Color;
import java.util.List;
import java.lang.Integer;
import java.util.Date;
import java.text.SimpleDateFormat;
import java.lang.StringBuilder;
import java.util.ArrayList;

/**
 * Shows all the currently logged in guilds
 * @author Nick
 */

@CommandData (
        defaultSyntax = "guildlist",
        aliases = {},
        category = CommandCategory.BOT_OWNER,
        permission = Permission.BOT_OWNER,
        description = "Will show all info about the current guilds",
        example = "show *will show info inline*"
        )

public class GuildList extends Command {

    @Override
    public void executeCommand(Message msg) {
        String timeStamp = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss").format(new Date());
        EmbedBuilder em = new EmbedBuilder();
        ArrayList<String> totalString = new ArrayList<String>(1);
        em.setTitle("All Guilds", null);
        Bot.getInstance().getBots()
        .forEach(j -> {
            j.getGuilds()
            .forEach(g -> {
                totalString.add("**Guild: " + g.getName()
                    + " ... Server ID: " + g.getId()+"**");
                totalString.add("Owner: " 
                    + Util.resolveNameFromMember(g.getOwner(),true)
                    + " ... Users: " 
                    + Integer.toString(g.getMembers().size()));
                totalString.add("Text Channels: " 
                    + Integer.toString(g.getTextChannels().size())
                    + " ... Voice Channels: " 
                    + Integer.toString(g.getVoiceChannels().size()));
                if (g.getJDA().getShardInfo() != null) {
                    totalString.add("Shard ID: " 
                        + g.getJDA().getShardInfo().getShardString());
                }
            });
        });

        MessageUtils.staggerArray(totalString,msg,em,Color.YELLOW);
    }
}