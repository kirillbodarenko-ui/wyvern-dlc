#!/bin/sh
# Dump the remaining 26.2 signatures the TotemPop / LivingEntityRendererMixin port needs.
JAVAP="/c/Program Files/Java/jdk-21.0.12/bin/javap"
JAR=".gradle/loom-cache/minecraftMaven/net/minecraft/minecraft-merged-8b9278343c/26.2/minecraft-merged-8b9278343c-26.2.jar"
OUT=api-entity2.txt
: > "$OUT"
for C in \
  net.minecraft.client.renderer.state.level.LevelRenderState \
  net.minecraft.client.renderer.entity.state.EntityRenderState \
  net.minecraft.client.renderer.entity.state.LivingEntityRenderState \
  net.minecraft.client.renderer.entity.state.AvatarRenderState \
  net.minecraft.client.renderer.entity.EntityRenderer \
  net.minecraft.client.renderer.state.level.CameraRenderState \
  net.minecraft.client.model.EntityModel \
  net.minecraft.client.model.Model ; do
  "$JAVAP" -p -cp "$JAR" "$C" >> "$OUT" 2>&1 || true
done
wc -l "$OUT"
