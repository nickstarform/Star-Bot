package io.ph.bot.commands.administration;

import java.awt.Color;

import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.bot.procedural.ProceduralAnnotation;
import io.ph.bot.procedural.ProceduralCommand;
import io.ph.bot.procedural.ProceduralListener;
import io.ph.bot.procedural.StepType;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;

/**
 * Various one-time configuration settings
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "configure",
        aliases = {"config"},
        category = CommandCategory.ADMINISTRATION,
        permission = Permission.MANAGE_SERVER,
        description = "Configure various settings for your server",
        example = "(no parameters)"
        )
@ProceduralAnnotation (
        title = "Bot configuration",
        steps = {"Limit $joinrole to a single role?",
                "Automatically delete invite links sent by non-moderator users?",
                "How many messages can a user send per 15 seconds? Use 0 to disable slow mode", "ID for the rules channel (if not present 0)", "ID for the mod report channel (if not present 0)"}, 
        types = {StepType.YES_NO, StepType.YES_NO, StepType.INTEGER, StepType.STRING, StepType.STRING},
        breakOut = "finish",
        deletePrevious = true
        )
public class Configure extends ProceduralCommand {

    public Configure(Message msg) {
        super(msg);
        super.setTitle(getTitle());
    }
    
    public Configure() {
        super(null);
    }

    @Override
    public void executeCommand(Message msg) {
        Configure instance = new Configure(msg);
        ProceduralListener.getInstance().addListener(msg, instance);
        instance.sendMessage(getSteps()[super.getCurrentStep()]);
    }

    @Override
    public void finish() {
        GuildObject g = GuildObject.guildMap.get(super.getStarter().getGuild().getId());
        g.getConfig().setLimitToOneRole((boolean) super.getResponses().get(0));
        g.getConfig().setDisableInvites((boolean) super.getResponses().get(1));
        g.getConfig().setMessagesPerFifteen((int) super.getResponses().get(2));
        g.getSpecialChannels().setRulesChannel((String) super.getResponses().get(3));
        g.getSpecialChannels().setReportChannel((String) super.getResponses().get(4));
        EmbedBuilder em = new EmbedBuilder();
        em.setTitle("Success", null)
        .setColor(Color.GREEN)
        .setDescription("Configured my settings for your server!");
        super.getStarter().getChannel().sendMessage(em.build()).queue();
        super.exit();
    }

}
