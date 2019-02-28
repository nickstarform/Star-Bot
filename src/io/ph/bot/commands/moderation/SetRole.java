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
        example = "[optional <rm>] [user <int>/<username>] [role-name <string>]"
        )
public class SetRole extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        String contents = Util.getCommandContents(msg);
        String param = Util.getParam(msg);
        String role = "";
        String id = "";
        Member mem;
        if (param.equalsIgnoreCase("rm")) {
            id = Util.getParam(contents);
            role = Util.getCommandContents(Util.getCommandContents(contents));
            param = "rm";
        } else {
            id = param;
            role = Util.getCommandContents(contents);
            param = "add";
        }
        // System.out.println(contents);
        // System.out.println(id);
        // System.out.println(role);
        // System.out.println(param);
        if (!Util.isInteger(id)) {
            mem = Util.resolveMemberFromMessage(id, msg.getGuild());
        } else {
            mem = Util.resolveUserFromMessage(id, msg.getGuild().getId());
        }
        String name = Util.resolveNameFromMember(mem);
        if (contents.split(" ").length < 2) {
            em.setTitle("Hmm...", null)
            .setColor(Color.RED)
            .setDescription("Improper inputs! User: <" + id + ">, role:<" + role + ">");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        if(role.equals("")) {
            MessageUtils.sendIncorrectCommandUsage(msg, this);
            return;
        }
        for(Role r : msg.getGuild().getRoles()) {
            if(r.getName().equalsIgnoreCase(role)) {
                if (mem.getRoles().contains(r) && param.equals("add")) {
                    em.setTitle("Hmm...", null)
                    .setColor(Color.YELLOW)
                    .setDescription("They're already in this role!");
                    msg.getChannel().sendMessage(em.build()).queue();
                    return;
                } else if (!mem.getRoles().contains(r) && param.equals("rm")) {
                    em.setTitle("Hmm...", null)
                    .setColor(Color.YELLOW)
                    .setDescription("They're not in this role!");
                    msg.getChannel().sendMessage(em.build()).queue();
                    return;
                } 
                if (param.equals("add")) {
                    final String responce = "You set " + name + " is now in the role **" + role + "**";
                    msg.getGuild().getController()
                    .addSingleRoleToMember(mem, r).queue(
                        success -> {
                            em.setTitle("Success", null)
                            .setColor(Color.GREEN)
                            .setDescription(responce);
                            msg.getChannel().sendMessage(em.build()).queue();
                        },
                        failure -> {
                            em.setTitle("Error", null)
                            .setColor(Color.RED)
                            .setDescription(failure.getMessage());
                            msg.getChannel().sendMessage(em.build()).queue();
                        });
                    return;
                } else {
                    final String responce = "You set " + name + " is removed from the role **" + role + "**";
                    msg.getGuild().getController()
                    .removeSingleRoleFromMember(mem, r).queue(
                        success -> {
                            em.setTitle("Success", null)
                            .setColor(Color.GREEN)
                            .setDescription(responce);
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
        }
        em.setTitle("Error", null)
        .setColor(Color.RED)
        .setDescription("That role doesn't exist!" + role);
        msg.getChannel().sendMessage(em.build()).queue();
    }
}
