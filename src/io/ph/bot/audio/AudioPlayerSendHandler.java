package io.ph.bot.audio;

import com.sedmelluq.discord.lavaplayer.player.AudioPlayer;
import com.sedmelluq.discord.lavaplayer.track.playback.AudioFrame;
import net.dv8tion.jda.api.audio.AudioSendHandler;

/**
 * This is a wrapper around AudioPlayer which makes it behave as an AudioSendHandler for JDA. As JDA calls canProvide
 * before every call to provide20MsAudio(), we pull the frame in canProvide() and use the frame we already pulled in
 * provide20MsAudio().
 */
import com.sedmelluq.discord.lavaplayer.format.OpusAudioDataFormat;
import net.dv8tion.jda.api.audio.AudioSendHandler;

public class AudioPlayerSendHandler implements AudioSendHandler {
  private final AudioPlayer audioPlayer;
  private AudioFrame lastFrame;

  /**
   * @param audioPlayer Audio player to wrap.
   */
  public AudioPlayerSendHandler(AudioPlayer audioPlayer) {
    this.audioPlayer = audioPlayer;
  }

  @Override
  public boolean canProvide() {
    lastFrame = audioPlayer.provide();
    return lastFrame != null;
  }

  @Override
  public byte[] provide20MsAudio() {
    return lastFrame.getData();
  }

  @Override
  public boolean isOpus() {
    return lastFrame != null && lastFrame.getFormat() instanceof OpusAudioDataFormat;
  }
}