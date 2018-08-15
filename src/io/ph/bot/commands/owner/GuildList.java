package io.ph.bot.commands.owner;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.jobs.StatusChangeJob;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.bot.Bot;

import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.EmbedBuilder;

import java.awt.Color;
import java.util.List;
import java.lang.Integer;
import java.util.Date;
import java.text.SimpleDateFormat;
import java.lang.StringBuilder;

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
        em.setTitle("All Guilds", null);
        Bot.getInstance().getBots()
        .forEach(j -> {
            j.getGuilds()
            .forEach(g -> {
                em.addField("Guild: ",g.getName(), false)
                .addField("Server ID", g.getId(), true)
                .addField("Owner: ",Util.resolveNameFromMember(g.getOwner(),true), true)
                .addField("Users", Integer.toString(g.getMembers().size()), true)
                .addField("Text Channels", Integer.toString(g.getTextChannels().size()), true)
                .addField("Voice Channels", Integer.toString(g.getVoiceChannels().size()), true);
                if (g.getJDA().getShardInfo() != null) {
                    em.addField("Shard ID", g.getJDA().getShardInfo().getShardString(), true);
                }
            });
        });

        em.setFooter("Message was sent Local time "+timeStamp, null)
        .setColor(Color.YELLOW);
        msg.getChannel().sendMessage(em.build()).queue(success -> {msg.delete().queue();});
    }
}