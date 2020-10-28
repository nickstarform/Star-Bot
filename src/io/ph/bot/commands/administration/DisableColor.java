package io.ph.bot.commands.administration;

import java.awt.Color;
import java.util.ArrayList;
import java.util.Set;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;

/**
 * disables the color role 
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "disablecolor",
        aliases = {"colordisable","stopcolor","colorstop"},
        category = CommandCategory.ADMINISTRATION,
        permission = Permission.MANAGE_ROLES,
        description = "Disallow users to create their own color role.",
        example = "delete *(**NON REVERSABLE**this will delete the color roles)"
        )
public class DisableColor extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        GuildObject g = GuildObject.guildMap.get(msg.getGuild().getId());
        boolean status = g.getConfig().isColorRoleStatus();        
        String param = Util.getCommandContents(msg);

        if ((param != null && !param.isEmpty())) {
            param = Util.getParam(msg);
        }
        // debug
        //System.out.println("status: <" + status + ">");

        if(!status) {
            em.setTitle("Disable Color", null)
            .setColor(Color.RED)
            .setDescription("Color is already disabled here");
        } else {
            g.getConfig().setColorRoleStatus(false);
            g.getConfig().setColorTemplateRoleId("");
            g.resetColorRole();
            em.setTitle("Disable Color", null)
            .setColor(Color.GREEN)
            .setDescription("Color is now disabled here");
        }
        if (param.equals("delete")) {
            Set<String> colorRoles = g.getColorJoinableRoles();
            ArrayList<String> delRoles = new ArrayList(colorRoles);
            for (int i = 0; i < delRoles.size(); i++) {
                try {
                    msg.getGuild().getRoleById(delRoles.get(i)).delete().queue();
                } catch(NullPointerException ex) {
                    continue;
                }
            }
            g.resetColorRole();
            em.setDescription("All color roles have been deleted and is disabled.");
        }

        MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
        msg.delete().queue();
    }
}
