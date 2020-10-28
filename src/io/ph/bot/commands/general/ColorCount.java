package io.ph.bot.commands.general;

import java.awt.Color;
import java.util.function.Supplier;
import java.util.Set;
import java.util.stream.Stream;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;
import io.ph.util.Util;
import io.ph.util.MessageUtils;

/**
 * List color roles, order by members, and set the color to the most popular role's
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "colorcount",
        aliases = {"colorlist", "colorstats"},
        category = CommandCategory.UTILITY,
        permission = Permission.NONE,
        description = "List all roles",
        example = "(no parameters)"
        )
public class ColorCount extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        GuildObject g = GuildObject.guildMap.get(msg.getGuild().getId());
        Set<String> colorRoles = g.getColorJoinableRoles();
        // debug
        //System.out.println("colorRoles: <" + colorRoles + ">");
        
        if(colorRoles.isEmpty()) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("Looks like your server doesn't have any Color roles!");
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
            msg.delete().queue();
            return;
        }
        StringBuilder sb = new StringBuilder();
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
        msg.getChannel().sendMessage(em.build()).queue();
    }

}
