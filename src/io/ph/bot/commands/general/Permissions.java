package io.ph.bot.commands.general;

import java.awt.Color;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.lang.StringBuilder;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.commands.CommandHandler;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import net.dv8tion.jda.core.EmbedBuilder;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.Member;

/**
 * Get help with commands
 * @author Nick
 */

/*
 *   NONE("No permissions", net.dv8tion.jda.core.Permission.MESSAGE_READ),
 *   KICK("Kick", net.dv8tion.jda.core.Permission.KICK_MEMBERS),
 *   BAN("Ban", net.dv8tion.jda.core.Permission.BAN_MEMBERS),
 *   MANAGE_ROLES("Manage roles", net.dv8tion.jda.core.Permission.MANAGE_ROLES),
 *   MANAGE_CHANNELS("Manage channels", net.dv8tion.jda.core.Permission.MANAGE_CHANNEL),
 *   MANAGE_SERVER("Manage server", net.dv8tion.jda.core.Permission.MANAGE_SERVER),
 *   ADMINISTRATOR("Administrator", net.dv8tion.jda.core.Permission.ADMINISTRATOR),
 *   BOT_OWNER("Bot owner", null);
 *   BOT_DEVELOPER("Bot developer", null);
*/

@CommandData (
        defaultSyntax = "permissions",
        aliases = {"permission","power"},
        category = CommandCategory.UTILITY,
        permission = Permission.NONE,
        description = "Tells users their server power level. Can target other users and send to pm vs inline",
        example = "<!power Nick show> or <!power Nick> or <!power>  "
        )

public class Permissions extends Command {

    @Override
    public void executeCommand(Message msg) {
        String temp = Util.getCommandContents(msg);
        String[] splited = temp.split("\\s+");
        String t = splited[0];
        Integer size = splited.length;
        Member target = null; // this is temporary name
        String authorname = msg.getAuthor().getName(); // author
        String suser = null; // this is the end target user to find power of
        
        // check user permissions. If has the bot owner permissions or if is the owner of the guild
        if (Util.memberHasPermission(msg.getGuild().getMember(msg.getAuthor()), Permission.ADMINISTRATOR) || (msg.getGuild().getMember(msg.getAuthor()).isOwner())) {
                // if use @
                if (msg.getMentionedUsers().size() > 0) {
                    target = msg.getGuild().getMember(msg.getMentionedUsers().get(0));
                    suser = msg.getGuild().getMember(msg.getMentionedUsers().get(0)).getEffectiveName();
                // if simple string
                } else if (Util.resolveMemberFromMessage(t, msg.getGuild()) != null) {
                    target = Util.resolveMemberFromMessage(t, msg.getGuild());
                    suser = Util.resolveMemberFromMessage(t, msg.getGuild()).getEffectiveName();
                // fallback to author    
                } else {
                    target = msg.getGuild().getMember(msg.getAuthor());
                    suser = authorname;
                }
        // fallback to author
        } else {
            target = msg.getGuild().getMember(msg.getAuthor());
            suser = authorname;
        };

        EmbedBuilder em = new EmbedBuilder();
        StringBuilder stringBuilder = new StringBuilder();

        for (Permission p : Permission.values()) {
            if (Util.memberHasPermission(target, p)) {
                stringBuilder.append(String.format("ALLOWED %s\n", p.name()));
            } else {
                stringBuilder.append(String.format("NOT ALLOWED %s\n", p.name()));
            }
        }
        // for testing, allow posting of permissions inline
         

        String finalString = stringBuilder.toString();
        StringBuilder stringDisplay = new StringBuilder();

        stringDisplay.append("These are the permissions for guild: ");
        stringDisplay.append(msg.getGuild().getName()+"");
        stringDisplay.append("\n");
        stringDisplay.append("For the user: ");
        stringDisplay.append(suser+"");
        String finalDisplay = stringDisplay.toString();

        /* 
        if asked print to screen
        otherwise print to DM
        */
        if (size > 1) {
                em.setTitle("Permissions", null)
                .setColor(Color.CYAN)
                .setDescription(finalDisplay)
                .addField("",finalString,true);
                msg.getChannel().sendMessage(em.build()).queue();
        } else {
            msg.getAuthor().openPrivateChannel().queue(success -> {
                em.setTitle("Permissions", null)
                .setColor(Color.CYAN)
                .setDescription(finalDisplay)
                .addField("",finalString,true);
            msg.getAuthor().openPrivateChannel().complete()
            .sendMessage(em.build()).queue(success1 -> {
                em.clearFields();
                em.setTitle("Success", null)
                .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                .setDescription("Check your PMs!");
                MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
                });
            msg.delete().queue();
            });     
        }
    }
}