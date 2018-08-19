package io.ph.bot.commands.general;

import java.awt.Color;
import java.util.function.Supplier;
import java.util.Set;
import java.util.stream.Stream;
import java.util.List;
import java.util.ArrayList;
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
import net.dv8tion.jda.core.entities.Role;
import net.dv8tion.jda.core.entities.Member;

/**
 * Leave role designated as joinable color
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "colorrole",
        aliases = {"color"},
        category = CommandCategory.UTILITY,
        permission = Permission.NONE,
        description = "Handles color roles for users\n"
                    + "`#hex` should be 7 characters including '#'",
        example = "`#hex` *(creates the role and puts user in it or just puts user in it)\n"
                + "`showall` *(shows all current color schemes with swatches)\n"
                + "`random` *(chooses a random color and assigns)\n"
                + "`remove/leave` *(clears the user from color roles in their name)\n"
                + "`remove #hex` *(users with manage role perms can remove this color role altogether)"
        )
public class ColorRole extends Command {
    private EmbedBuilder em;
    private Message msg;
    private String contents;
    private GuildObject g;
    private Set<String> colorRoles;
    private int del = 0;
    private String param;
    private String options;
    private List<Role> guildRoles;
    private List<Role> memberRoles;

    @Override
    public void executeCommand(Message msg) {
        this.msg = msg;
        this.em = new EmbedBuilder();
        this.contents = Util.getCommandContents(msg).trim();
        this.g = GuildObject.guildMap.get(msg.getGuild().getId());
        this.colorRoles = g.getColorJoinableRoles();
        this.guildRoles = msg.getGuild().getRoles();
        this.memberRoles = msg.getMember().getRoles();

        if(contents.equals("")) {
            MessageUtils.sendIncorrectCommandUsage(msg, this);
            msg.delete().queue();
            em.clear();
            return;
        } 
        if (!g.getConfig().isColorRoleStatus()) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("Color is disabled here");
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
            msg.delete().queue();
            em.clear();
            return;
        }

        this.param = Util.getParam(msg);
        this.options = contents.replace(param,"").trim();
        // debug
        //System.out.println("param: <" + param + ">");
        //System.out.println("contents: <" + contents + ">");
        //System.out.println("options: <" + options + ">");

        /*

        */
        if(param.equalsIgnoreCase("remove") || 
                  param.equalsIgnoreCase("leave")) {
            deleteColor(options);
            pruneColor();
        } else if(param.equalsIgnoreCase("random")) {
            options = randomColor();
            createColor(options);
            joinColor(options);
            pruneColor();
        } else if (param.equalsIgnoreCase("showall")) {
            pruneColor();
            listColor();
        } else if (param.equalsIgnoreCase("prune")) {
            pruneColor();
        } else {
            createColor(param);
            joinColor(param);
            pruneColor();
        }
        if (em == null) {
            MessageUtils.sendIncorrectCommandUsage(msg, this);
            msg.delete().queue();
            em.clear();
        }
    }

    /**
    * Creates this random color. 
    * @param colRole String with the name of the role to create
    */
    private String randomColor() {
        //System.out.println("randomColor");

        return Util.color2Hex(Util.randomColor()).toUpperCase();
    }

    /**
    * Creates this role. 
    * @param colRole String with the name of the role to create
    */
    private void createColor(String colRole) {
        // debug
        //System.out.println("createColor");
        //System.out.println("colRole: <" + colRole + ">");

        Role finRole = null;

        if(colRole.equals("") || !colRole.startsWith("#") || (colRole.length() != 7)) {
            em.clear();
            return ;
        }

        while (msg.getGuild().getRolesByName(colRole,true).isEmpty()) {
            Role template = msg.getGuild().getRoleById(g.getConfig().getColorTemplateRoleId());
            msg.getGuild().getController().createCopyOfRole(template).setName(colRole.toUpperCase()).setColor(Util.hex2Rgb(colRole)).complete();

        }
        // debug
        //System.out.println("createdRole: <" + colRole + ">");
        
        finRole = msg.getGuild().getRolesByName(colRole,true).get(0);
        g.addColorRole(finRole.getId());
        handleColorOrder(finRole);
    }

    /**
    * Joins this role. If you are in 
    * another color it will remove that one first
    * @param colRole String with the name of the role to join
    */
    private void joinColor(String colRole) {
        // debug
        //System.out.println("joinColor");
        //System.out.println("joinRole: <" + colRole + ">");

        if(colRole.equals("") || !colRole.startsWith("#") || (colRole.length() != 7)) {
            em.clear();
            return;
        }


        if (Util.roleNameFromList(memberRoles).contains(colRole)) {
            em.setTitle("Hmm...", null)
            .setColor(Color.CYAN)
            .setDescription("You're already in this role!");      
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
            em.clear();
            msg.delete().queue();
            return;
        }
        if(g.getConfig().isLimitToOneRole()) {
            Set<String> userRoles = memberRoles
                    .stream()
                    .map(Role::getId)
                    .collect(Collectors.toSet());
            if(userRoles.stream()
                    .filter(s -> 
                        g.getColorJoinableRoles().contains(s))
                    .count() > 0) {
                em.setTitle("Error", null)
                .setColor(Color.RED)
                .setDescription("You cannot join more than one role!");
                MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
                em.clear();
                msg.delete().queue();
                return;
            }
        }

        guildRoles = msg.getGuild().getRoles();
        //System.out.println("Joining....");
        //System.out.println("guildRoles: " + Util.roleNameFromList(guildRoles));
        //System.out.println("Found: " + Util.roleNameFromList(guildRoles).contains(colRole));
        if (Util.roleNameFromList(guildRoles).contains(colRole)) {
            // Make sure the roles are uniquely set
            while (hasColorRole(msg.getMember())) {
                deleteColor("");
            }
            //System.out.println("Joining....");

            Role r = msg.getGuild().getRolesByName(colRole,true).get(0);
            msg.getGuild().getController()
            .addRolesToMember(msg.getMember(),r).complete();
            em.setTitle("Success", null)
            .setColor(r.getColor())
            .setDescription("You are now in the role **" + r.getName() + "**");
                   
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
            em.clear();
            msg.delete().queue();
        } else {
        em.setTitle("Error", null)
        .setColor(Color.RED)
        .setDescription("That role doesn't exist or isn't joinable");
        }
    }

    /**
    * Deletes either the role or deletes the role from the user
    * @param delRole String with the name of the role to delete
    */
    private void deleteColor(String delRole) {

        // debug
        //System.out.println("deleteColor");
        //System.out.println("delRole: <" + delRole + ">");

        /*
        */
        if(!delRole.equals("") 
            && delRole.startsWith("#") 
            && (delRole.length() == 7) 
            && Util.memberHasPermission(msg.getMember(),Permission.MANAGE_ROLES)) {
            if (!g.isColorJoinableRole(msg.getGuild().getRolesByName(delRole,true).get(0).getId())) {
                em.setTitle("Not a color role that I have: " + delRole, null)
                .setColor(Color.RED);
                return;
            } else {
                g.removeColorRole(msg.getGuild().getRolesByName(delRole,true).get(0).getId());
                msg.getGuild().getRolesByName(delRole,true).get(0).delete().queue();
                em.setTitle("Deleted Role: " + delRole, null)
                .setColor(Color.RED)
                .setDescription("Color role has been deleted.");
            }
        } else {
            List<Role> delRoles = new ArrayList<Role>(0);
            for (Role r : memberRoles){
                if (g.isColorJoinableRole(r.getId())) {
                    delRoles.add(r);
                }
            }

            //System.out.println("roles: " + Util.roleNameFromList(memberRoles));
            List<Role> roles = memberRoles;

            roles = Util.removeFromList(roles,delRoles);
            // debug
            //System.out.println("roles: " + Util.roleNameFromList(roles));
            //System.out.println("delRoles: " + Util.roleNameFromList(delRoles));

            msg.getGuild().getController()
                .modifyMemberRoles(msg.getMember(), roles).complete();
        }
  
        // debug
        if (param.toLowerCase() == "remove"){
            em.setTitle("Success", null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
            .setDescription("You are now removed from the color roles.");
        }

        if (!em.isEmpty()){
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
            em.clear();
            msg.delete().queue(); 
        }
        return;
    }

    /**
    * Deletes either the role or deletes the role from the user
    * @param delRole String with the name of the role to delete
    */
    private void pruneColor() {
        // remove any empty color roles
        
        for (Role r: msg.getGuild().getRoles()) {
            if (g.isColorJoinableRole(r.getId()) && (msg.getGuild().getMembersWithRoles(r).size() == 0)) {
                // debug
                //System.out.println("pruning role: " + r.getName());
                r.delete().complete();
                g.removeColorRole(r.getId());
            }
        }
    }

    /**
    * Lists all the colors available
    * <p>
    * TODO: allow it to make images of swatches
    */
    private void listColor() {
        colorRoles = g.getColorJoinableRoles();

        if(colorRoles.isEmpty()) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("Looks like your server doesn't have any Color roles!");
            return;
        } else {
            StringBuilder sb = new StringBuilder();
            // for now the same as ColorCount but want to get it to create an image with the swatches
            Supplier<Stream<String>> stream = () -> colorRoles.stream().sorted((a, b) -> {
                return Integer.compare(msg.getGuild().getMembersWithRoles(msg.getGuild().getRoleById(b)).size(),(msg.getGuild().getMembersWithRoles(msg.getGuild().getRoleById(a)).size()));
                });
            stream.get().forEach(s -> {
                sb.append(String.format("**%s** | %d\n", msg.getGuild().getRoleById(s).getName(), 
                        msg.getGuild().getMembersWithRoles(msg.getGuild().getRoleById(s)).size()));
            });

            em.setTitle("Color ranking", null)
            .setColor(msg.getGuild().getRoleById(stream.get().findFirst().get()).getColor())
            .setDescription(sb.toString());
        }
        MessageUtils.sendMessage(msg.getChannel().getId(),em.build());
        em.clear();
        msg.delete().queue();
    }

    /**
    * This is the color handler. This organizes the role color
    * <p>
    */
    private void handleColorOrder(Role role) {

        Role template = msg.getGuild().getRoleById(g.getConfig().getColorTemplateRoleId());

        msg.getGuild().getController().modifyRolePositions().selectPosition(role).moveTo(template.getPosition()).complete();

        return;
    }

    /**
    * This will handles determining if member has color role
    * <p>
    */
    private boolean hasColorRole(Member mem) {
        List<Role> roles = mem.getRoles();
        for (Role r : roles){
            if (g.isColorJoinableRole(r.getId())) {
                return true;
            }
        }

        return false;
    } 

}
