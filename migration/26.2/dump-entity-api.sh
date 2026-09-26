#!/bin/sh
# Dump the 26.2 signatures the TotemPop / LivingEntityRendererMixin port needs.
set -e
JAVAP="/c/Program Files/Java/jdk-21.0.12/bin/javap"
JAR=".gradle/loom-cache/minecraftMaven/net/minecraft/minecraft-merged-8b9278343c/26.2/minecraft-merged-8b9278343c-26.2.jar"
OUT=api-entity.txt
: > "$OUT"
for C in \
  net.minecraft.client.renderer.LevelRenderer \
  net.minecraft.client.renderer.entity.EntityRenderDispatcher \
  net.minecraft.client.renderer.entity.LivingEntityRenderer \
  net.minecraft.client.renderer.entity.player.AvatarRenderer \
  net.minecraft.client.renderer.SubmitNodeCollector \
  net.minecraft.client.renderer.OrderedSubmitNodeCollector ; do
  "$JAVAP" -p -cp "$JAR" "$C" >> "$OUT" 2>&1 || true
done
wc -l "$OUT"
