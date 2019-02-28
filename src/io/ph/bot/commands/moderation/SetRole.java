package io.ph.bot.commands.moderation;

import java.awt.Color;
import java.util.Set;
import java.util.stream.Collectors;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.util.MessageUtils;
import io.ph.util.Util;
import net.dv8tion.jda.core.EmbedBuilder;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.Member;
import net.dv8tion.jda.core.entities.Role;

/**
 * Allow moderators to assign roles to others
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "setrole",
        aliases = {},
        category = CommandCategory.MODERATION,
        permission = Permission.MANAGE_ROLES,
        description = "Assign a role to a user",
        example = "[userid <int>] [role-name <string>]"
        )
public class SetRole extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        String contents = Util.getCommandContents(msg);
        String role = Util.getCommandContents(contents);
        String id = Util.getParam(msg);
        if ((contents.split(" ").length < 2) || (!Util.isInteger(id))) {
            em.setTitle("Hmm...", null)
            .setColor(Color.RED)
            .setDescription("Improper inputs! ID: <" + id + ">, role:<" + role + ">");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        Member mem = Util.resolveUserFromMessage(id, msg.getGuild().getId());
        if(role.equals("")) {
            MessageUtils.sendIncorrectCommandUsage(msg, this);
            return;
        }
        for(Role r : msg.getGuild().getRoles()) {
            if(r.getName().equalsIgnoreCase(role)) {
                if (mem.getRoles().contains(r)) {
                    em.setTitle("Hmm...", null)
                    .setColor(Color.CYAN)
                    .setDescription("They're already in this role!");
                    msg.getChannel().sendMessage(em.build()).queue();
                    return;
                }
                msg.getGuild().getController()
                .addRolesToMember(mem, r).queue(
                    success -> {
                        em.setTitle("Success", null)
                        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                        .setDescription("You set " + Util.resolveNameFromMember(mem) + " is now in the role **" + role + "**");
                        msg.getChannel().sendMessage(em.build()).queue();
                    },
                    failure -> {
                        em.setTitle("Error", null)
                        .setColor(Color.RED)
                        .setDescription(failure.getMessage());
                        msg.getChannel().sendMessage(em.build()).queue();
                    });
                return;
            }
        }
        em.setTitle("Error", null)
        .setColor(Color.RED)
        .setDescription("That role doesn't exist!");
        msg.getChannel().sendMessage(em.build()).queue();
    }
}
