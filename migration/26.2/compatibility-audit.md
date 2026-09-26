# Minecraft 26.2 compatibility audit

Checked the target Minecraft JAR, including inherited members and nested class imports.

Missing imported classes: 11

Access-widener entries requiring adaptation: 1/47

## Missing imports

- `com.mojang.blaze3d.platform.GlStateManager.DestFactor` (1 files)
- `com.mojang.blaze3d.platform.GlStateManager.SourceFactor` (1 files)
- `com.mojang.blaze3d.vertex.BufferUploader` (23 files)
- `net.minecraft.client.renderer.CompiledShaderProgram` (2 files)
- `net.minecraft.client.renderer.CoreShaders` (15 files)
- `net.minecraft.client.renderer.FogParameters` (1 files)
- `net.minecraft.client.renderer.MultiBufferSource` (11 files)
- `net.minecraft.client.renderer.MultiBufferSource.BufferSource` (1 files)
- `net.minecraft.client.renderer.RenderStateShard` (1 files)
- `net.minecraft.client.renderer.ShaderProgram` (2 files)
- `net.minecraft.client.renderer.block.BlockRenderDispatcher` (1 files)

## Invalid access-widener entries

```text
accessible	field	com/mojang/blaze3d/pipeline/RenderTarget	depthBufferId	I
```

This audit does not validate injection points, runtime behavior, or render output. A successful audit alone is not a completed port.
