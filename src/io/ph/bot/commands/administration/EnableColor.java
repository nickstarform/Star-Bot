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
import net.dv8tion.jda.api.entities.Role;

/**
 * Enables the color role 
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "enablecolor",
        aliases = {"colorenable","startcolor","colorstart"},
        category = CommandCategory.ADMINISTRATION,
        permission = Permission.MANAGE_ROLES,
        description = "Allow users to create their own color role. "
                    + "Must define a template-role that already exists.\n"
                    + "When enabling color via `colorenable templaterole` the template role must be *ABOVE* the highest positioned *COLORED* role. If anything is higher and has non-default colors, the color role wont show for those users in that role.",
        example = "template-role *(Name of the role whose permissions you want to copy)"
        )
public class EnableColor extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        GuildObject g = GuildObject.guildMap.get(msg.getGuild().getId());
        boolean status = g.getConfig().isColorRoleStatus();
        String param = Util.getCommandContents(msg);

        if(param.equals("")) {
            MessageUtils.sendIncorrectCommandUsage(msg, this);
            msg.delete().queue();
            em=null;
        }
        param = Util.getParam(msg);
        String template = msg.getGuild().getRolesByName(param,true).get(0).getId();
        // debug
        //System.out.println("template: <" + template + ">");

        if(g.getConfig().isColorRoleStatus()) {
            em.setTitle("Enable Color", null)
            .setColor(Color.RED)
            .setDescription("Color permissions is already enabled here");
        } else {
            g.getConfig().setColorRoleStatus(true);
            g.getConfig().setColorTemplateRoleId(template);
            em.setTitle("Enable Color", null)
            .setColor(Color.GREEN)
            .setDescription("Color permissions is now enabled here");
        }

        ArrayList<String> detRoles = new ArrayList<String>(0);
        for(Role r : msg.getGuild().getRoles()) {
            if((r.getName().startsWith("#") && (r.getName().length() == 7))
                    || g.isColorJoinableRole(r.getId())) { 
                detRoles.add(r.getName());
                if (!g.isColorJoinableRole(r.getId())) {
                    g.addColorRole(r.getId());
                }
            }
        }

        if (detRoles.size() > 0) {
            em.addField("Detected Color Roles: ",
                Util.combineStringArray(detRoles),true);
        } else {
            Set<String> colorRoles = g.getColorJoinableRoles();
            ArrayList<String> delRoles = new ArrayList(colorRoles);
            for (int i = 0; i < colorRoles.size(); i++) {
                g.removeColorRole(delRoles.get(i));
            }
        }

        MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
        msg.delete().queue();
    }

}
