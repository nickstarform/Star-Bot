package io.ph.bot.commands.administration;

import java.awt.Color;

import java.util.ArrayList;
import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.TextChannel;

/**
 * Allows bot to ignore certain channels
 * @author Nick
 */
@CommandData (
        defaultSyntax = "ignorechannel",
        aliases = {"ignore"},
        category = CommandCategory.ADMINISTRATION,
        permission = Permission.MANAGE_CHANNELS,
        description = "Set the bot to ignore a channel",
        example = "(no option sets to current channel)\n"
                + "channelId *(The channel id for the bot to ignore)\n"
                + "list *(list all ignored channels)\n"
                + "reset *(resets all ignored channels)"
        )
public class IgnoreChannel extends Command {

    private GuildObject g;
    private EmbedBuilder em;
    private Message msg;

    @Override
    public void executeCommand(Message msg) {
        this.msg = msg;
        this.em = new EmbedBuilder();
        this.g = GuildObject.guildMap.get(msg.getGuild().getId());
        String param = Util.getParam(msg).toUpperCase().trim();
        String contents = "";
        if (!param.equals("")) {
            contents = Util.getCommandContents(msg).toUpperCase().replace(param,"").trim();
        }

        if (param.equals("RESET")) {
            g.resetIgnoreChannel();
            em.setTitle("Ignored Channels Reset", null)
            .setColor(Color.YELLOW)
            .setDescription("Full discord server ignored channels are reset.");
        } else if (param.equals("REMOVE") || param.equals("DELETE")) {
            g.removeIgnoreChannel(msg.getGuild().getTextChannelById(contents).getId());
            em.setTitle("Channel removed from ignored list", null)
            .setColor(Color.YELLOW);
        } else if (param.equals("LIST")) {
            ArrayList<String> names = Util.channelNameFromList(msg.getGuild(), g.getIgnoreChannel());
            em.setTitle("Ignored Channels", null);
            if (names.size() > 0) {
                em.setColor(Color.GREEN)
                .addField("Names: ",Util.combineStringArray(names),false);
            } else {
                em.setColor(Color.RED)
                .setDescription("No ignored channels are set."); 
            }
        } else if (!param.equals("")) {
            try {
                param = msg.getGuild().getTextChannelById(param).getId();
                setChannel(param);
            } catch (NullPointerException e) {
                em.setTitle("Channel Not Found", null)
                .setColor(Color.YELLOW);
            }
        } else {
            setChannel(msg.getChannel().getId());
        }

        MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
        msg.delete().queue();
    }

    /**
    * Creates this random color. 
    * @param colRole String with the name of the role to create
    */
    private void setChannel(String param) {
        TextChannel txt = msg.getGuild().getTextChannelById(param);
        if (g.isIgnoreChannel(param)) {
            if (g.removeIgnoreChannel(param)) {
                em.setTitle("Ignore Channel Removed", null)
                .setColor(Color.GREEN)
                .setDescription("The Ignore Channel has been lifted: " + txt.getName() + " <" + txt.getId() + ">");
            } else {
                em.setTitle("Ignore Channel Failed", null)
                .setColor(Color.RED)
                .setDescription("Couldn't remove the channel: " + txt.getName() + " <" + txt.getId() + ">");
            }
        } else {
            if (g.addIgnoreChannel(param)) {
                em.setTitle("Ignore Channel Added", null)
                .setColor(Color.GREEN)
                .setDescription("The Ignore Channel has been added: " + txt.getName() + " <" + txt.getId() + ">");
            } else {
                em.setTitle("Ignore Channel Failed", null)
                .setColor(Color.RED)
                .setDescription("Couldn't add the channel: " + txt.getName() + " <" + txt.getId() + ">");
            }
        }
    }
}
