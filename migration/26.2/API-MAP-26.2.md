# Old API → New API map for Minecraft 26.2 (render / shader classes)

Scope: the render and shader classes that **no longer exist** in 26.2, and what replaces each one.
Audience: the agents porting the 12 remaining files.

## Sources and method

Everything below was checked against one of three grounds:

1. **The real 26.2 jar** — `C:\Users\Karitsa\.gradle\caches\fabric-loom\minecraftMaven\net\minecraft\minecraft-merged-deobf\26.2\minecraft-merged-deobf-26.2.jar`,
   inspected with `jar tf` (31,707 entries enumerated) followed by
   `javap -p -cp <jar> <FQCN>` using `C:\Users\Karitsa\Desktop\wyvern-dlc\.tools\java25\jdk-25.0.4.1+1\bin\javap.exe`.
2. **Already-ported source in this repo** under `migration\26.2\src\main\java\wtf\wyvern\utility\render\` and friends.
3. **Existing API dumps** in `migration\26.2\*.txt` and `.codex_tmp_migration\*.txt`.

"Absent" claims are backed by an exhaustive grep of the full jar class list, not by a single failed lookup.

### Confidence legend

| Tag | Meaning |
|---|---|
| `verified-by-javap` | Class/field/method was printed by `javap` from the 26.2 jar. Exact signature quoted. |
| `verified-by-port` | The idiom is used by code in this repo that is already ported and compiles against 26.2. |
| `inferred` | Follows from verified surrounding API but was not itself printed by `javap`. |
| `unknown` | Not resolved. Do not guess — treat as an open question. |

---

## 1. Quick mapping table

| Old symbol (does not exist in 26.2) | Replacement | Confidence |
|---|---|---|
| `com.mojang.blaze3d.vertex.BufferUploader` | `MeshBuilder` + `GpuMeshRenderer` (this repo) → `CommandEncoder`/`RenderPass` | verified-by-port |
| `com.mojang.blaze3d.vertex.BufferUploader.drawWithShader(MeshData)` | `GpuMeshRenderer.draw(MeshData, RenderPipeline, TextureSetup, Matrix4f, Map<String,ByteBuffer>)` | verified-by-port |
| `net.minecraft.client.renderer.MultiBufferSource` / `.BufferSource` | `SubmitNodeCollector` / `OrderedSubmitNodeCollector` (+ extract/submit split) | verified-by-javap |
| `RenderBuffers.bufferSource()` | **removed**; `RenderBuffers` now only exposes `fixedBufferPack()`, `sectionBufferPool()`, `stagedVertexBuffer()`, `endFrame()`, `close()` | verified-by-javap |
| `net.minecraft.client.renderer.CoreShaders` | `net.minecraft.resources.Identifier` of the form `core/<name>` passed to `RenderPipeline.Builder.withVertexShader/withFragmentShader`, or a `RenderPipelines.*` constant | verified-by-javap + verified-by-port |
| `net.minecraft.client.renderer.ShaderProgram` | **removed**; the pair of shader `Identifier`s inside a `RenderPipeline` | verified-by-javap |
| `net.minecraft.client.renderer.CompiledShaderProgram` | `com.mojang.blaze3d.pipeline.CompiledRenderPipeline` (only `boolean isValid()`), obtained from `GpuDevice.precompilePipeline(RenderPipeline)` | verified-by-javap |
| `net.minecraft.client.renderer.RenderStateShard` / `.ShaderStateShard` | **removed**; state is now baked into a `com.mojang.blaze3d.pipeline.RenderPipeline` | verified-by-javap |
| `RenderStateShard.ShaderStateShard` (used by `GlProgram.renderPhaseProgram()`) | drop the method; expose `GlProgram.pipeline()` returning `RenderPipeline` | inferred |
| `net.minecraft.client.renderer.fog.FogParameters` | `net.minecraft.client.renderer.fog.FogData` | verified-by-javap |
| `net.minecraft.client.renderer.block.BlockRenderDispatcher` | `BlockModelResolver` + `BlockModelRenderState.submit(...)` / `ModelBlockRenderer.tesselateBlock(...)` | verified-by-javap |
| `com.mojang.blaze3d.platform.GlStateManager.SourceFactor` / `.DestFactor` | single enum `com.mojang.blaze3d.platform.BlendFactor`, declared in the pipeline via `BlendFunction` | verified-by-javap |
| `com.mojang.blaze3d.platform.GlStateManager` | `com.mojang.blaze3d.opengl.GlStateManager` (raw-GL helpers only) | verified-by-javap |
| `RenderSystem.setShader(...)` | **removed** | verified-by-javap |
| `RenderSystem.setShaderTexture(int, Identifier)` / `(int, int)` | **removed**; use `TextureSetup` + `RenderPass.bindTexture` | verified-by-javap |
| `RenderSystem.setShaderColor(...)` | **removed**; use vertex colours or `DynamicUniforms.writeTransform(Matrix4f, Vector4f)` | verified-by-javap |
| `RenderSystem.blendFunc(...)` / `defaultBlendFunc()` / `enableBlend()` / `disableBlend()` | **removed**; blending is a pipeline property (`ColorTargetState` + `BlendFunction`) | verified-by-javap |
| `RenderSystem.lineWidth(float)` | **removed**; line width is a vertex attribute (`DefaultVertexFormat.POSITION_COLOR_NORMAL_LINE_WIDTH` + `BufferBuilder.setLineWidth`) | verified-by-javap |
| `RenderSystem.enableCull()` / `disableCull()` | **removed**; `RenderPipeline.Builder.withCull(boolean)` | verified-by-javap |
| `RenderSystem.getProjectionMatrix()` | **removed**; use `RenderSystem.getProjectionMatrixBuffer()` (returns `GpuBufferSlice`) or your own `Projection` UBO | verified-by-javap |
| `RenderSystem.setProjectionMatrix(Matrix4f, ProjectionType)` | `RenderSystem.setProjectionMatrix(GpuBufferSlice, ProjectionType)` | verified-by-javap |
| `Minecraft.getMainRenderTarget()` | `Minecraft.getInstance().gameRenderer.mainRenderTarget()` | verified-by-javap |
| `RenderTarget.bindRead()` / `unbindRead()` / `bindWrite(boolean)` | **removed**; use `CommandEncoder.createRenderPass(...)` | verified-by-javap |
| `RenderTarget.blitToScreen(int,int)` | `RenderTarget.blitAndBlendToTexture(GpuTextureView color, GpuTextureView depth)` | verified-by-javap |
| `RenderTarget.getColorTextureId()` (was already stale) | `RenderTarget.getColorTextureView()` / `getColorTexture()` | verified-by-javap |
| `Tesselator` | `MeshBuilder` (this repo) → `ByteBufferBuilder` + `BufferBuilder` | verified-by-javap + verified-by-port |
| `ShaderManager.getProgramForLoading(ShaderProgram)` / `getProgram(...)` | **removed**; `ShaderManager` keeps only `getShader(Identifier, ShaderType)`, `getPostChain(Identifier, Set<Identifier>)`, `getName()`, `close()` | verified-by-javap |
| `Font.drawInBatch(...)` | `Font.prepareText(...)` → `Font.PreparedText`; or `OrderedSubmitNodeCollector.submitText(...)` | verified-by-javap |
| `Uniform` immediate setter API | **removed** — `com.mojang.blaze3d.opengl.Uniform` is now an empty marker interface (`close()` only). Use UBOs. | verified-by-javap |

---

## 2. `com.mojang.blaze3d.vertex.BufferUploader` — **removed**

`jar tf` grep over the whole 26.2 class list returns no `BufferUploader` entry of any package. Confidence: `verified-by-javap`.

There is no drop-in method replacement. The immediate "upload my `MeshData` and draw it now" operation is now a three-step render-pass sequence, and the repo already wraps that in one helper.

### Verified replacement surface (this repo)

`C:\Users\Karitsa\Desktop\wyvern-dlc\migration\26.2\src\main\java\wtf\wyvern\utility\render\GpuMeshRenderer.java`

```java
public static void draw(MeshData mesh,
                        RenderPipeline pipeline,
                        TextureSetup textures,
                        Matrix4f modelView,
                        Map<String, ByteBuffer> uniformData)
```

It takes ownership of `mesh` (wraps it in try-with-resources), asserts the vertex format and topology match the pipeline, uploads vertices/indices/uniforms through `CommandEncoder.transientMemory().uploadGpu(...)`, opens a `RenderPass`, binds `DynamicTransforms` + caller uniforms + `Sampler0..2`, and calls `drawIndexed(state.indexCount(), 1, firstIndex, 0, 0)`. Confidence: `verified-by-port`.

`...\utility\render\MeshBuilder.java` replaces `Tesselator`:

```java
public static MeshBuilder getInstance();                       // singleton, render-thread only
public BufferBuilder begin(PrimitiveTopology topology, VertexFormat format);
public static void release();
```

Backed by one `new ByteBufferBuilder(786432)`. Confidence: `verified-by-port`.

### Before / after

Before (`DrawUtil.java`):

```java
RenderSystem.enableBlend();
RenderSystem.defaultBlendFunc();
RenderSystem.setShader(CoreShaders.POSITION_COLOR);
BufferBuilder builder = new BufferBuilder(...);
// ... addVertex ...
BufferUploader.drawWithShader(builder.buildOrThrow());
RenderSystem.disableBlend();
```

After (idiom from `Render3DUtil` / `WorldMeshes`):

```java
BufferBuilder builder = MeshBuilder.getInstance()
        .begin(PrimitiveTopology.QUADS, DefaultVertexFormat.POSITION_COLOR);
// ... addVertex ...
WorldMeshes.draw(builder.buildOrThrow(), null /*texture*/, false /*additive*/, true /*depth*/);
```

`WorldMeshes.draw` builds/caches the pipeline and forwards to `GpuMeshRenderer.draw`. For a bespoke
pipeline (custom shader + UBO), call `GpuMeshRenderer.draw(mesh, pipeline, textures, RenderSystem.getModelViewMatrixCopy(), Map.of("Param", byteBuffer))` directly, as `WorldMsdfDraw` and `FullScreenPass.draw` do.

**Important:** with `BufferUploader` gone, the ~20 call sites in `DrawUtil.java` and the ones in `Render2DUtil.java`, `TargetESP.java`, `Satan.java`, `Cosmetics.java`, `ShaderHandsRenderer.java`, `HandShaderRenderer.java` must each be converted to an explicit pipeline; there is no flag to "just upload".

---

## 3. `net.minecraft.client.renderer.MultiBufferSource` (+ `MultiBufferSource.BufferSource`) — **removed**

Absent from the jar class list. Confidence: `verified-by-javap`.

Two distinct usages exist in this repo and they map to two different things:

### 3a. Drawing text/entities into the world (`TotemPop`, `CrystalAura`)

The whole "immediate batched consumer" concept is gone. 26.2 splits entity rendering into
**extract** then **submit**:

```java
// verified-by-javap, net.minecraft.client.renderer.entity.EntityRenderDispatcher
public <E extends Entity> EntityRenderState extractEntity(E entity, float partialTick);
public <S extends EntityRenderState> void submit(S state,
        net.minecraft.client.renderer.state.level.CameraRenderState cameraRenderState,
        double x, double y, double z,
        com.mojang.blaze3d.vertex.PoseStack poseStack,
        net.minecraft.client.renderer.SubmitNodeCollector collector);
```

`EntityRenderDispatcher` has **no** `render(...)` method any more. Confidence: `verified-by-javap`.

`RenderBuffers` no longer has `bufferSource()`:

```java
// verified-by-javap, net.minecraft.client.renderer.RenderBuffers
public SectionBufferBuilderPack fixedBufferPack();
public SectionBufferBuilderPool sectionBufferPool();
public StagedVertexBuffer stagedVertexBuffer();
public void endFrame();
public void close();
```

World text uses the collector instead of `Font.drawInBatch(...)`:

```java
// verified-by-javap, net.minecraft.client.renderer.OrderedSubmitNodeCollector
public abstract void submitText(PoseStack poseStack, float x, float y,
        net.minecraft.util.FormattedCharSequence text, boolean dropShadow,
        net.minecraft.client.gui.Font.DisplayMode displayMode,
        int lightCoords, int color, int backgroundColor, int outlineColor);
```

`net.minecraft.client.renderer.SubmitNodeStorage` is the only implementation of the collector in the
jar (`implements SubmitNodeCollector`). Confidence: `verified-by-javap`. It is constructed by the
level renderer, not by mods.

### 3b. `renderChinaHat(PoseStack, MultiBufferSource, ...)` style method parameters (`Cosmetics`)

Change the parameter type to `net.minecraft.client.renderer.SubmitNodeCollector` (or
`OrderedSubmitNodeCollector`). `submitModel(...)` replaces the old "dispatcher.render with a
`MultiBufferSource`" call:

```java
// verified-by-javap, OrderedSubmitNodeCollector
public <S> void submitModel(net.minecraft.client.model.Model<? super S> model, S state,
        PoseStack poseStack, net.minecraft.client.renderer.rendertype.RenderType renderType,
        int lightCoords, int overlayCoords, int color,
        net.minecraft.client.renderer.texture.TextureAtlasSprite sprite,
        int outlineColor,
        net.minecraft.client.renderer.feature.ModelFeatureRenderer.CrumblingOverlay crumbling);
public default <S> void submitModel(Model<? super S>, S, PoseStack, RenderType, int, int, int, CrumblingOverlay);
public default <S> void submitModel(Model<? super S>, S, PoseStack, net.minecraft.resources.Identifier, int, int, int, CrumblingOverlay);
```

### Before / after

Before (`TotemPop.java`):

```java
MultiBufferSource.BufferSource immediate = mc.renderBuffers().bufferSource();
dispatcher.render(entity, x, y, z, tickDelta, matrices, immediate, 0xF000F0);
immediate.endBatch();
```

After — there is no batching object to end. The equivalent work is done inside the level-render
collector, so a module that wants to draw an extra entity must either (a) submit through a collector
it received, or (b) build its own geometry and draw it with `GpuMeshRenderer`.

```java
EntityRenderState state = dispatcher.extractEntity(entity, tickDelta);
// hand `state` to a collector for the current frame, e.g. inside a LevelRenderer submit phase:
dispatcher.submit(state, cameraRenderState, x, y, z, poseStack, submitNodeCollector);
```

When no collector is available (the usual case for a module running from a Fabric world-render
callback), route (b) is the portable answer: build a `MeshData` via `MeshBuilder` and draw it with
`GpuMeshRenderer`. Confidence: `verified-by-javap` for the API; the choice between (a) and (b) is an
`inferred` design decision.

**Gap:** whether a mod can legitimately obtain a `SubmitNodeCollector` during a Fabric
`WorldRenderEvents` callback is **unknown** (no public factory was found). Do not assume one exists.

---

## 4. `net.minecraft.client.renderer.CoreShaders` — **removed**

Absent from the jar. Confidence: `verified-by-javap`.

Shader identity in 26.2 is a bare `net.minecraft.resources.Identifier` resolved from the
`assets/<ns>/shaders/` tree, with the vanilla core shaders living under the `minecraft:core/`
namespace. It is passed to the pipeline:

```java
// verified-by-javap, com.mojang.blaze3d.pipeline.RenderPipeline$Builder
public RenderPipeline.Builder withVertexShader(net.minecraft.resources.Identifier);
public RenderPipeline.Builder withVertexShader(java.lang.String);
public RenderPipeline.Builder withFragmentShader(net.minecraft.resources.Identifier);
public RenderPipeline.Builder withFragmentShader(java.lang.String);
```

The two constants this repo actually used map as follows:

| Old | New `Identifier` |
|---|---|
| `CoreShaders.POSITION_COLOR` | `Identifier.withDefaultNamespace("core/position_color")` |
| `CoreShaders.POSITION_TEX_COLOR` | `Identifier.withDefaultNamespace("core/position_tex_color")` |
| (lines) | `Identifier.withDefaultNamespace("core/rendertype_lines")` |

Confidence: `verified-by-port` (`WorldMeshes.pipeline` uses exactly these three strings).

`Identifier` factories, verified-by-javap:

```java
public static Identifier withDefaultNamespace(String path);
public static Identifier fromNamespaceAndPath(String namespace, String path);
public String getPath();
public String getNamespace();
```

### Before / after

Before:

```java
RenderSystem.setShader(CoreShaders.POSITION_TEX_COLOR);
RenderSystem.setShaderTexture(0, identifier);
BufferUploader.drawWithShader(builder.buildOrThrow());
```

After (`WorldMeshes` idiom — note the texture moves into `TextureSetup`, not a global slot):

```java
RenderPipeline pipeline = WorldMeshes.pipelineFor(texturedOrNot, ...);   // built once, cached
GpuMeshRenderer.draw(builder.buildOrThrow(), pipeline,
        TextureSetup.singleTexture(
                mc.getTextureManager().getTexture(identifier).getTextureView(),
                mc.getTextureManager().getTexture(identifier).getSampler()),
        RenderSystem.getModelViewMatrixCopy(), Map.of());
```

---

## 5. `net.minecraft.client.renderer.ShaderProgram` — **removed**

Absent from the jar. Confidence: `verified-by-javap`.

The old `new ShaderProgram(id.withPrefix("core/"), vertexFormat, ShaderDefines.EMPTY)` value object no
longer exists. Its three fields are now separate parts of the pipeline:

* shader identity → `withVertexShader(Identifier)` / `withFragmentShader(Identifier)`
* vertex format → `withVertexBinding(int index, VertexFormat format)`
* shader defines → `withShaderDefine(String)` / `withShaderDefine(String, int)` / `withShaderDefine(String, float)`

`RenderPipeline` accessors, verified-by-javap:

```java
public Identifier getLocation();
public Identifier getVertexShader();
public Identifier getFragmentShader();
public net.minecraft.client.renderer.ShaderDefines getShaderDefines();
public com.mojang.blaze3d.vertex.VertexFormat[] getVertexFormatBindings();
public com.mojang.blaze3d.vertex.VertexFormat getVertexFormatBinding(int index);
public com.mojang.blaze3d.PrimitiveTopology getPrimitiveTopology();
public boolean isCull();  public com.mojang.blaze3d.platform.PolygonMode getPolygonMode();
public com.mojang.blaze3d.pipeline.ColorTargetState getColorTargetState();
public com.mojang.blaze3d.pipeline.ColorTargetState[] getColorTargetStates();
public com.mojang.blaze3d.pipeline.DepthStencilState getDepthStencilState();
public java.util.List<com.mojang.blaze3d.pipeline.BindGroupLayout> getBindGroupLayouts();
public boolean wantsDepthTexture();
public int getSortKey();
```

`ShaderDefines` still exists at `net.minecraft.client.renderer.ShaderDefines` (with an inner
`ShaderDefines.Builder`) — verified-by-javap.

### Mapping for `GlProgram.java`

| Old member | New member |
|---|---|
| `ShaderProgram programKey` | `RenderPipeline pipeline` (or the `Identifier`s + format to build one) |
| `new ShaderProgram(id.withPrefix("core/"), format, ShaderDefines.EMPTY)` | `RenderPipeline.builder().withLocation(...).withVertexShader(id)/.withFragmentShader(id).withVertexBinding(0, format).build()` |
| `mc.getShaderManager().getProgramForLoading(programKey)` | nothing equivalent — see §6 |
| `RenderStateShard renderPhaseProgram()` | delete; callers take `pipeline()` directly |
| `RenderSystem.setShader(programKey)` | delete; pass `pipeline()` to `GpuMeshRenderer.draw` |
| `findUniform(name)` | wrap in a `GlUniform`-style CPU-side record and feed a `PARAMETERS` UBO (see §12) |

`ShaderManager` in 26.2, verified-by-javap — this is all that remains:

```java
public net.minecraft.client.renderer.PostChain getPostChain(net.minecraft.resources.Identifier, java.util.Set<net.minecraft.resources.Identifier>);
public java.lang.String getShader(net.minecraft.resources.Identifier, com.mojang.blaze3d.shaders.ShaderType);
public java.lang.String getName();
public void close();
```

`getProgramForLoading(...)`, `getProgram(...)` and the `ShaderManager.CompilationException` throwing
load path are gone. Loading is now implicit: build a `RenderPipeline`, hand it to a `RenderPass`, and
the device compiles it lazily (or eagerly via `GpuDevice.precompilePipeline`). Confidence:
`verified-by-javap` for the removals; the lazy-compile statement is `inferred`.

---

## 6. `net.minecraft.client.renderer.CompiledShaderProgram` — **removed**

Absent from the jar. Confidence: `verified-by-javap`.

The nearest surviving type is:

```java
// verified-by-javap
public interface com.mojang.blaze3d.pipeline.CompiledRenderPipeline {
  boolean isValid();
}
```

obtained from:

```java
// verified-by-javap, com.mojang.blaze3d.systems.GpuDevice
public com.mojang.blaze3d.pipeline.CompiledRenderPipeline precompilePipeline(RenderPipeline);
public com.mojang.blaze3d.pipeline.CompiledRenderPipeline precompilePipeline(RenderPipeline, com.mojang.blaze3d.shaders.ShaderSource);
public void clearPipelineCache();
```

**Critical finding for `ShaderProgramAccessor`:** `CompiledRenderPipeline` exposes **only**
`boolean isValid()`. There is no uniforms map, no program id, no attribute list. The accessor
`@Accessor Map<String, Uniform> getUniformsByName()` on `CompiledShaderProgram` has **no target and no
equivalent** — it must be deleted, not repaired. Confidence: `verified-by-javap`.

Also verified-by-javap: `com.mojang.blaze3d.opengl.Uniform` still exists but is now an **empty marker
interface** with a single `default void close()`. The old per-uniform `.set(...)` API is gone, so
`GlProgram.findUniform(...)` cannot work as written. See §12 for the replacement (CPU-side uniform
records packed into a UBO block).

---

## 7. `net.minecraft.client.renderer.RenderStateShard` — **removed**

Absent from the jar (no `RenderStateShard`, no `RenderStateShard$ShaderStateShard`, no other inner
class). Confidence: `verified-by-javap`.

All render state that used to be set per draw is now declared once on the pipeline. Full builder
surface, verified-by-javap:

```java
public static RenderPipeline.Builder RenderPipeline.builder(RenderPipeline.Snippet... snippets);

public RenderPipeline.Builder withLocation(String);
public RenderPipeline.Builder withLocation(Identifier);
public RenderPipeline.Builder withVertexShader(String | Identifier);
public RenderPipeline.Builder withFragmentShader(String | Identifier);
public RenderPipeline.Builder withShaderDefine(String);
public RenderPipeline.Builder withShaderDefine(String, int);
public RenderPipeline.Builder withShaderDefine(String, float);
public RenderPipeline.Builder withBindGroupLayout(BindGroupLayout);
public RenderPipeline.Builder withPolygonMode(com.mojang.blaze3d.platform.PolygonMode);
public RenderPipeline.Builder withCull(boolean);
public RenderPipeline.Builder withColorTargetState(ColorTargetState);
public RenderPipeline.Builder withColorTargetState(int index, ColorTargetState);
public RenderPipeline.Builder withUnusedColorTargetState(int index);
public RenderPipeline.Builder withDepthStencilState(DepthStencilState);
public RenderPipeline.Builder withDepthStencilState(Optional<DepthStencilState>);
public RenderPipeline.Builder withVertexBinding(int index, VertexFormat);
public RenderPipeline.Builder withPrimitiveTopology(PrimitiveTopology);
public RenderPipeline.Snippet buildSnippet();
public RenderPipeline build();
```

State value types, all verified-by-javap:

```java
public final class ColorTargetState extends Record {
  public static final ColorTargetState DEFAULT;
  public static final int WRITE_RED, WRITE_GREEN, WRITE_BLUE, WRITE_ALPHA, WRITE_COLOR, WRITE_ALL, WRITE_NONE;
  public ColorTargetState(BlendFunction blendFunction);                        // Optional<BlendFunction> variant exists too
  public ColorTargetState(Optional<BlendFunction>, com.mojang.blaze3d.GpuFormat, int writeMask);
  public Optional<BlendFunction> blendFunction();  public com.mojang.blaze3d.GpuFormat format();  public int writeMask();
}

public final class DepthStencilState extends Record {
  public static final DepthStencilState DEFAULT;
  public DepthStencilState(CompareOp depthTest, boolean writeDepth);
  public DepthStencilState(CompareOp depthTest, boolean writeDepth, float depthBiasScaleFactor, float depthBiasConstant);
}

public final class BlendFunction extends Record {
  public static final BlendFunction LIGHTNING, GLINT, OVERLAY, TRANSLUCENT,
      TRANSLUCENT_PREMULTIPLIED_ALPHA, ADDITIVE, ENTITY_OUTLINE_BLIT, INVERT;
  public BlendFunction(BlendFactor src, BlendFactor dst);
  public BlendFunction(BlendFactor src, BlendFactor dst, com.mojang.blaze3d.platform.BlendOp);
  public BlendFunction(BlendFactor, BlendFactor, BlendOp, BlendFactor, BlendFactor, BlendOp);
  public BlendFunction(com.mojang.blaze3d.pipeline.BlendEquation);
  public BlendFunction(BlendEquation color, BlendEquation alpha);
}

public enum CompareOp { ALWAYS_PASS, LESS_THAN, LESS_THAN_OR_EQUAL, EQUAL, NOT_EQUAL,
                        GREATER_THAN_OR_EQUAL, GREATER_THAN, NEVER_PASS }
```

`RenderPipeline.Snippet` (record) is the reusable fragment produced by `buildSnippet()`. Accessors,
verified-by-javap: `vertexShader()`, `fragmentShader()`, `shaderDefines()`, `bindGroupLayouts()`,
`colorTargetStates()`, `activeColorTargetStateCount()`, `depthStencilState()`, `polygonMode()`,
`cull()`, `vertexFormatPerBuffer()`, `vertexFormatMode()`.

### Before / after

Before:

```java
RenderStateShard shard = new RenderStateShard.ShaderStateShard(programKey);
RenderSystem.enableBlend();
RenderSystem.defaultBlendFunc();
RenderSystem.enableCull();
RenderSystem.lineWidth(width);
```

After (the repo's own `WorldMeshes` pattern — one cached pipeline per state combination):

```java
var builder = RenderPipeline.builder()
        .withLocation(Identifier.fromNamespaceAndPath("wyvern", "world/texture_false_true_quads"))
        .withVertexShader(Identifier.withDefaultNamespace("core/position_tex_color"))
        .withFragmentShader(Identifier.withDefaultNamespace("core/position_tex_color"))
        .withVertexBinding(0, DefaultVertexFormat.POSITION_TEX_COLOR)
        .withPrimitiveTopology(PrimitiveTopology.QUADS)
        .withColorTargetState(new ColorTargetState(BlendFunction.TRANSLUCENT))
        .withDepthStencilState(Optional.of(new DepthStencilState(CompareOp.LESS_THAN_OR_EQUAL, false)))
        .withCull(false);
builder.withBindGroupLayout(bindings.build());
RenderPipeline pipeline = builder.build();
```

---

## 8. `net.minecraft.client.renderer.fog.FogParameters` — **removed**

Absent from the jar. Confidence: `verified-by-javap`.

Replacement, verified-by-javap:

```java
// net.minecraft.client.renderer.fog.FogData — plain public fields, no methods
public class FogData {
  public float environmentalStart;
  public float renderDistanceStart;
  public float environmentalEnd;
  public float renderDistanceEnd;
  public float skyEnd;
  public float cloudEnd;
  public org.joml.Vector4f color;
  public FogData();
}

// net.minecraft.client.renderer.fog.FogRenderer
public static final int FOG_UBO_SIZE;
public FogData setupFog(net.minecraft.client.Camera camera, int renderDistance,
                        net.minecraft.client.DeltaTracker deltaTracker, float partialTick,
                        net.minecraft.client.multiplayer.ClientLevel level);
public void updateBuffer(FogData data);
public com.mojang.blaze3d.buffers.GpuBufferSlice getBuffer(FogRenderer.FogMode mode);
public void endFrame();
public void close();
public static boolean toggleFog();
```

Fog is no longer part of the shader state at draw time. `FogRenderer` owns a ring buffer, `setupFog`
produces a `FogData`, `updateBuffer` writes it, and `getBuffer(mode)` yields the `GpuBufferSlice` that
`RenderSystem.setShaderFog(GpuBufferSlice)` consumes:

```java
// verified-by-javap, RenderSystem — the only fog entry points left
public static void setShaderFog(com.mojang.blaze3d.buffers.GpuBufferSlice);
public static com.mojang.blaze3d.buffers.GpuBufferSlice getShaderFog();
```

A pipeline that wants fog declares the `BindGroupLayouts.FOG` layout (see §11) and binds the slice
with `pass.setUniform("Fog", slice)`. Camera fog state is also mirrored on
`CameraRenderState.fogData` / `CameraRenderState.fogType` (verified-by-javap).

`STATUS.md` records that the repo's own fog work (disabling effect fog) is already done via
`MobEffectFogEnvironment`; the abstract API is `net.minecraft.client.renderer.fog.environment.FogEnvironment`.
Confidence for the `FogEnvironment` detail: `inferred` (not javap'd here).

`compatibility-audit.md` lists 1 file importing `FogParameters`, but a repo-wide grep found **no**
current usage site. Treat that audit row as stale. Confidence: `verified-by-javap` (absence of class) / observation.

---

## 9. `net.minecraft.client.renderer.block.BlockRenderDispatcher` — **removed**

Absent from the jar. Confidence: `verified-by-javap`.

The old "give me a `VertexConsumer` and I'll tessellate the block" dispatcher is gone. 26.2 splits it
into model resolution and model tessellation:

```java
// verified-by-javap, net.minecraft.client.renderer.block.BlockModelResolver
public BlockModelResolver(net.minecraft.client.resources.model.ModelManager modelManager);
public void update(net.minecraft.client.renderer.block.BlockModelRenderState state,
                   net.minecraft.world.level.block.state.BlockState blockState,
                   net.minecraft.client.renderer.block.model.BlockDisplayContext context);
public void updateForItemFrame(BlockModelRenderState state, boolean flag1, boolean flag2);

// verified-by-javap, net.minecraft.client.renderer.block.model.BlockDisplayContext
public static BlockDisplayContext create();

// verified-by-javap, net.minecraft.client.renderer.block.BlockModelRenderState
public void submit(com.mojang.blaze3d.vertex.PoseStack, net.minecraft.client.renderer.SubmitNodeCollector, int, int, int);
public void submitOnlyOutline(PoseStack, SubmitNodeCollector, int, int, int);
public void submitWithZOffset(PoseStack, SubmitNodeCollector, int, int, int);
public boolean isEmpty();
public void clear();
public java.util.List<net.minecraft.client.renderer.block.dispatch.BlockStateModelPart> setupModel(org.joml.Matrix4fc, boolean);
public int blockLightCoords;

// verified-by-javap, net.minecraft.client.renderer.block.ModelBlockRenderer
public ModelBlockRenderer(boolean ambientOcclusion, boolean cull, net.minecraft.client.color.block.BlockColors);
public void tesselateBlock(net.minecraft.client.renderer.block.BlockQuadOutput output,
                           float x, float y, float z,
                           net.minecraft.client.renderer.block.BlockAndTintGetter level,
                           net.minecraft.core.BlockPos pos,
                           net.minecraft.world.level.block.state.BlockState state,
                           net.minecraft.client.renderer.block.dispatch.BlockStateModel model,
                           long seed);

// verified-by-javap, net.minecraft.client.renderer.block.BlockStateModelSet
public net.minecraft.client.renderer.block.dispatch.BlockStateModel get(BlockState);
public net.minecraft.client.renderer.block.dispatch.BlockStateModel missingModel();

// verified-by-javap, net.minecraft.client.renderer.block.BlockQuadOutput
public interface BlockQuadOutput {
  void put(float x, float y, float z,
           net.minecraft.client.resources.model.geometry.BakedQuad quad,
           com.mojang.blaze3d.vertex.QuadInstance instance);
}
```

`EntityRenderDispatcher` keeps a `BlockModelResolver blockModelResolver` field (verified-by-javap),
which is where a module can obtain one.

### Before / after

Before:

```java
BlockRenderDispatcher dispatcher = Minecraft.getInstance().getBlockRenderer();
dispatcher.renderSingleBlock(state, poseStack, bufferSource, light, overlay);
```

After:

```java
BlockModelRenderState state = new BlockModelRenderState();
resolver.update(state, blockState, BlockDisplayContext.create());
state.submit(poseStack, submitNodeCollector, light, overlay, 0 /*outline*/);
```

Again, the submit route needs a `SubmitNodeCollector`; from a module callback you would instead
collect quads via a `BlockQuadOutput` and push them through `MeshBuilder` + `GpuMeshRenderer`
(`inferred`).

`compatibility-audit.md` lists 1 file importing `BlockRenderDispatcher`, but a repo-wide grep found
**no** current usage site. Treat as stale.

---

## 10. `GlStateManager.SourceFactor` / `GlStateManager.DestFactor`, and `GlStateManager`'s new home

Verified-by-javap:

* `com.mojang.blaze3d.platform.GlStateManager` — **not in the jar**.
* `com.mojang.blaze3d.opengl.GlStateManager` — **present**, and it is a raw-GL helper only. Every
  member is either a `gl*`/`_gl*` passthrough or a `_`-prefixed cached-state setter:
  `_disableScissorTest()`, `_enableScissorTest()`, `_scissorBox(int,int,int,int)`, `_disableDepthTest()`,
  `_enableDepthTest()`, `_depthFunc(int)`, `_depthMask(boolean)`, `_disableBlend(int)`,
  `_enableBlend(int)`, `_blendFuncSeparate(int,int,int,int)`, `_blendEquationSeparate(int,int)`,
  `_enableCull()`, `_disableCull()`, `_polygonMode(int,int)`, `_colorMask(int)`, `_colorMask(int,int)`,
  `_viewport(int,int,int,int)`, `_clear(int)`, `_activeTexture(int)`, `_bindTexture(int)`, …
* `SourceFactor` and `DestFactor` enums — **gone**. There is exactly one blend-factor enum:

```java
// verified-by-javap
public final class com.mojang.blaze3d.platform.BlendFactor extends Enum<BlendFactor> {
  CONSTANT_ALPHA, CONSTANT_COLOR, DST_ALPHA, DST_COLOR, ONE, ONE_MINUS_CONSTANT_ALPHA,
  ONE_MINUS_CONSTANT_COLOR, ONE_MINUS_DST_ALPHA, ONE_MINUS_DST_COLOR, ONE_MINUS_SRC_ALPHA,
  ONE_MINUS_SRC_COLOR, SRC_ALPHA, SRC_ALPHA_SATURATE, SRC_COLOR, ZERO
}
```

Blend factors are never set at draw time; they are components of a `BlendFunction` record that lives on
the pipeline's `ColorTargetState` (see §7).

### Mapping table for the call sites in `Satan.java` / `Cosmetics.java`

| Old call | New expression |
|---|---|
| `RenderSystem.blendFunc(SRC_ALPHA, ONE_MINUS_SRC_ALPHA)` | `new ColorTargetState(BlendFunction.TRANSLUCENT)` |
| `RenderSystem.defaultBlendFunc()` | `new ColorTargetState(BlendFunction.TRANSLUCENT)` (that is what the default was) |
| `RenderSystem.blendFunc(SRC_ALPHA, ONE)` (additive) | `new ColorTargetState(BlendFunction.ADDITIVE)` — **or** `new BlendFunction(BlendFactor.SRC_ALPHA, BlendFactor.ONE)`, which is the form `WorldMeshes` actually uses |
| `RenderSystem.blendFunc(GL11.GL_SRC_ALPHA, GL11.GL_ONE_MINUS_SRC_ALPHA)` | same as `TRANSLUCENT` |
| `RenderSystem.enableBlend()` / `disableBlend()` | pipeline has, or does not have, a `BlendFunction` on its `ColorTargetState` |

`WorldMeshes` uses the explicit two-factor constructor for additive:
`new BlendFunction(BlendFactor.SRC_ALPHA, BlendFactor.ONE)` (verified-by-port). The equivalence of
`BlendFunction.ADDITIVE` to that pair is `inferred`, not javap-verified — prefer the explicit
constructor unless you have checked `ADDITIVE`'s record components.

`_enableBlend(int)` / `_disableBlend(int)` / `_blendFuncSeparate(int,int,int,int)` on the new
`GlStateManager` are internal backend helpers; a mod should not call them.

---

## 11. Render-pass architecture: `RenderPipeline`, `CommandEncoder`, `RenderPass`

### `RenderPipeline` — verified-by-javap, full constructor

```java
protected RenderPipeline(net.minecraft.resources.Identifier location,
                         net.minecraft.resources.Identifier vertexShader,
                         net.minecraft.resources.Identifier fragmentShader,
                         net.minecraft.client.renderer.ShaderDefines shaderDefines,
                         java.util.List<com.mojang.blaze3d.pipeline.BindGroupLayout> bindGroupLayouts,
                         com.mojang.blaze3d.pipeline.ColorTargetState[] colorTargetStates,
                         com.mojang.blaze3d.pipeline.DepthStencilState depthStencilState,
                         com.mojang.blaze3d.platform.PolygonMode polygonMode,
                         boolean cull,
                         com.mojang.blaze3d.vertex.VertexFormat[] vertexFormatPerBuffer,
                         com.mojang.blaze3d.PrimitiveTopology primitiveTopology,
                         int sortKey);
```

Use `RenderPipeline.builder(...)`, not the constructor (it is `protected`).

### `CommandEncoder` — verified-by-javap

```java
public void submit();
public com.mojang.blaze3d.systems.TransientMemory transientMemory();
public RenderPass createRenderPass(Supplier<String> label, GpuTextureView color, Optional<Vector4fc> clearColor);
public RenderPass createRenderPass(Supplier<String> label, GpuTextureView color, Optional<Vector4fc> clearColor,
                                   GpuTextureView depth, OptionalDouble clearDepth);
public RenderPass createRenderPass(Supplier<String> label, GpuTextureView color, Optional<Vector4fc> clearColor,
                                   GpuTextureView depth, OptionalDouble clearDepth, RenderPass.RenderArea area);
public RenderPass createRenderPass(com.mojang.blaze3d.systems.RenderPassDescriptor descriptor);
public void clearColorTexture(GpuTexture, Vector4fc);
public void clearColorAndDepthTextures(GpuTexture, Vector4fc, GpuTexture, double);
public void clearColorAndDepthTextures(GpuTexture, Vector4fc, GpuTexture, double, int, int, int, int);
public void clearDepthTexture(GpuTexture, double);
public void writeToBuffer(GpuBufferSlice, java.nio.ByteBuffer);
public void copyToBuffer(GpuBufferSlice, GpuBufferSlice);
public void writeToTexture(GpuTexture, NativeImage);
public void writeToTexture(GpuTexture, java.nio.ByteBuffer, int, int, int, int, int, int);
public void copyBufferToTexture(GpuBufferSlice, int, int, int, int, GpuTexture, int, int, int, int, int, int);
public void copyTextureToBuffer(GpuTexture, GpuBuffer, long, Runnable, int);
public void copyTextureToTexture(GpuTexture src, GpuTexture dst, int, int, int, int, int, int, int);
public com.mojang.blaze3d.buffers.GpuFence createFence();
```

### `RenderPass` — verified-by-javap

```java
public void setPipeline(RenderPipeline);
public void bindTexture(String name, GpuTextureView, GpuSampler);
public void setUniform(String name, com.mojang.blaze3d.buffers.GpuBuffer);
public void setUniform(String name, com.mojang.blaze3d.buffers.GpuBufferSlice);
public void setVertexBuffer(int index, GpuBufferSlice);
public void setIndexBuffer(com.mojang.blaze3d.buffers.GpuBuffer, com.mojang.blaze3d.IndexType);
public void drawIndexed(int indexCount, int instanceCount, int firstIndex, int baseVertex, int firstInstance);
public void draw(int vertexCount, int instanceCount, int firstVertex, int firstInstance);
public void multiDrawIndexed(java.nio.IntBuffer, int, int, int);
public void multiDrawIndexed(org.lwjgl.PointerBuffer, java.nio.IntBuffer, java.nio.IntBuffer, int);
public void drawIndexedIndirect(GpuBufferSlice, int);
public <T> void drawMultipleIndexed(Collection<RenderPass.Draw<T>>, GpuBuffer, IndexType, Collection<String>, T);
public void enableScissor(int x, int y, int w, int h);
public void disableScissor();
public void pushDebugGroup(Supplier<String>);
public void popDebugGroup();
public void close();
```

The argument order of `drawIndexed` (indexCount, instanceCount, firstIndex, baseVertex, firstInstance)
is corroborated by the game's own `GuiRenderer` and is noted in `STATUS.md`.

### Canonical usage (this repo, `GpuMeshRenderer`)

```java
var encoder = RenderSystem.getDevice().createCommandEncoder();
GpuBufferSlice vertices = encoder.transientMemory().uploadGpu(mesh.vertexBuffer(), 4, GpuBuffer.USAGE_VERTEX);
// ... indices ...
GpuBufferSlice transforms = RenderSystem.getDynamicUniforms().writeTransform(modelView);
try (RenderPass pass = pipeline.getDepthStencilState() == null
        ? encoder.createRenderPass(() -> "Wyvern mesh", color, Optional.empty())
        : encoder.createRenderPass(() -> "Wyvern mesh", color, Optional.empty(), depth, OptionalDouble.empty())) {
    pass.setPipeline(pipeline);
    RenderSystem.bindDefaultUniforms(pass);
    pass.setUniform("DynamicTransforms", transforms);
    pass.setVertexBuffer(0, vertices);
    pass.setIndexBuffer(indices, indexType);
    pass.drawIndexed(state.indexCount(), 1, firstIndex, 0, 0);
}
encoder.submit();
```

Confidence: `verified-by-port`.

### Render-target I/O

`RenderTarget` survives at `com.mojang.blaze3d.pipeline.RenderTarget`, verified-by-javap:

```java
public int width;  public int height;  public final boolean useDepth;
public void resize(int, int);
public void destroyBuffers();
public void copyDepthFrom(RenderTarget);
public void createBuffers(int, int);
public void blitAndBlendToTexture(GpuTextureView color, GpuTextureView depth);
public GpuTexture getColorTexture();      public GpuTextureView getColorTextureView();
public GpuTexture getDepthTexture();      public GpuTextureView getDepthTextureView();
```

`com.mojang.blaze3d.pipeline.TextureTarget extends RenderTarget` still exists with the constructor
`TextureTarget(String label, int width, int height, boolean useDepth, com.mojang.blaze3d.GpuFormat)` —
note this is a **5-arg** constructor; the old repo code's `new TextureTarget(1920, 1024, false)` is gone.
Confidence: `verified-by-javap`.

Replacements for the old FBO API:

| Old | New |
|---|---|
| `mc.getMainRenderTarget()` | `Minecraft.getInstance().gameRenderer.mainRenderTarget()` |
| `MAIN_FBO.bindRead()` / `unbindRead()` / `bindWrite(boolean)` | open a `RenderPass` on `MAIN_FBO.getColorTextureView()` (+ `getDepthTextureView()`) |
| `MAIN_FBO.blitToScreen(w, h)` | `MAIN_FBO.blitAndBlendToTexture(colorView, depthView)` |
| `fbo.getColorTextureId()` (int GL name) | `fbo.getColorTextureView()` |
| `RenderSystem.outputColorTextureOverride` | still present and public — `public static GpuTextureView outputColorTextureOverride;` plus `outputDepthTextureOverride` |

`Minecraft` itself has **no** render-target accessor in 26.2 (verified-by-javap: no `RenderTarget`
appears anywhere in its member list). `Minecraft.getWindow()` still exists.

---

## 12. Frame memory and buffers: `MeshData`, `ByteBufferBuilder`, `BufferBuilder`, `StagingBuffer`, `UberGpuBuffer`

### `MeshData` — verified-by-javap

```java
public class MeshData implements AutoCloseable {
  public MeshData(ByteBufferBuilder.Result vertexBuffer, MeshData.DrawState drawState);
  public java.nio.ByteBuffer vertexBuffer();
  public java.nio.ByteBuffer indexBuffer();          // null when the mesh relies on a sequential index buffer
  public ByteBufferBuilder.Result vertexBufferSlice();
  public MeshData.DrawState drawState();
  public MeshData.SortState sortQuads(ByteBufferBuilder, VertexSorting);
  public void close();
}

public final class MeshData.DrawState extends Record {
  public VertexFormat format();
  public int vertexCount();
  public int indexCount();
  public com.mojang.blaze3d.PrimitiveTopology primitiveTopology();
  public com.mojang.blaze3d.IndexType indexType();
}
```

Purpose: the CPU-side result of building geometry, owned by the caller. `close()` frees the backing
`ByteBufferBuilder` slot — the reason `GpuMeshRenderer.draw` takes ownership and wraps it in
try-with-resources.

### `ByteBufferBuilder` — verified-by-javap

```java
public class ByteBufferBuilder implements AutoCloseable {
  public ByteBufferBuilder(int initialCapacity);
  public ByteBufferBuilder(int initialCapacity, long maxCapacity);
  public static ByteBufferBuilder exactlySized(int);
  public long reserve(int bytes);
  public ByteBufferBuilder.Result build();
  public void clear();
  public void discard();
  public void close();
}
```

Purpose: a growable native arena backing transient vertex data. This is what replaces the old
`Tesselator`'s internal buffer. The repo keeps one per `MeshBuilder`, sized `786432` bytes
(verified-by-port).

### `BufferBuilder` — verified-by-javap

```java
public class BufferBuilder implements com.mojang.blaze3d.vertex.VertexConsumer {
  public BufferBuilder(ByteBufferBuilder storage, com.mojang.blaze3d.PrimitiveTopology, VertexFormat);
  public MeshData build();
  public MeshData buildOrThrow();
  public VertexConsumer addVertex(float, float, float);
  public VertexConsumer setColor(int r, int g, int b, int a);
  public VertexConsumer setColor(int argb);
  public VertexConsumer setUv(float, float);
  public VertexConsumer setUv1(int, int);
  public VertexConsumer setOverlay(int);
  public VertexConsumer setUv2(int, int);
  public VertexConsumer setLight(int);
  public VertexConsumer setNormal(float, float, float);
  public VertexConsumer setLineWidth(float);
  public void addVertex(float x, float y, float z, int color, float u, float v,
                        int overlay, int light, float nx, float ny, float nz);
}
```

Note the constructor is now `(ByteBufferBuilder, PrimitiveTopology, VertexFormat)` — the old
`Tesselator`-bound constructor is gone.

### `StagingBuffer` — verified-by-javap

```java
public abstract class StagingBuffer implements AutoCloseable {
  public static StagingBuffer create(String label, com.mojang.blaze3d.systems.GpuDevice device, int size);
  public StagingBuffer.BufferHandle tryAppend(java.nio.ByteBuffer data);
  protected abstract java.nio.ByteBuffer getWriteBuffer();
  protected abstract void copyTo(CommandEncoder, GpuBuffer, long, long, long);
  protected void rotateBuffer();
  public StagingBuffer.Uploader startUploading(CommandEncoder encoder);
  public abstract void close();
}
```

Purpose: a rotating CPU→GPU transfer arena for data that is uploaded once and reused across frames
(as opposed to `TransientMemory`, which is per-frame). Subclass `StagingBuffer.Cpu` exists for the
CPU-managed variant, and `StagingBuffer.PersistentlyMapped` for a persistently mapped GPU buffer
(both present in the jar). `BufferHandle` carries `offset`/`size` and `close()` returns the slot.
`Uploader.copyTo(BufferHandle, GpuBuffer, long)` performs the actual copy inside a
`try (var uploader = stagingBuffer.startUploading(encoder))` block. Confidence:
`verified-by-javap` for the members; the "reuse across frames" characterization is `inferred`.

### `UberGpuBuffer<T>` — verified-by-javap

```java
public class UberGpuBuffer<T> implements AutoCloseable {
  public UberGpuBuffer(String label, int bufferUsage, int heapSize, int alignSize, StagingBuffer stagingBuffer);
  public <U extends T> boolean addAllocation(U key, UberGpuBuffer.UploadCallback<U> callback, java.nio.ByteBuffer data);
  public boolean uploadStagedAllocations(GpuDevice device, StagingBuffer.Uploader uploader);
  public TlsfAllocator.Allocation getAllocation(T key);
  public void removeAllocation(T key);
  public com.mojang.blaze3d.buffers.GpuBuffer getGpuBuffer(TlsfAllocator.Allocation);
  public void printStatistics();
  public void close();
}
```

Purpose: a single large GPU buffer subdivided by a **TLSF allocator**
(`com.mojang.blaze3d.vertex.TlsfAllocator`) so many small objects (sprites, glyphs, per-entity data)
share one upload and one bind. Vanilla uses it for the font glyph atlas and the sprite atlas. This is
almost certainly **not** needed by the 12 files being ported; it is listed here because the task asked
for it. Confidence: `verified-by-javap` for members; "used for font/sprite atlases" is `inferred`.

### `TransientMemory` (the per-frame path `GpuMeshRenderer` uses) — verified-by-javap

```java
public interface com.mojang.blaze3d.systems.TransientMemory {
  default ByteBuffer allocateCpu(long size, long alignment);
  default GpuBufferSlice.MappedView allocateStaging(long, long, int usage);
  default GpuBufferSlice allocateGpu(long, long, int usage);
  default GpuBufferSlice.MappedView allocateGpuMapped(long, long, int usage);
  default GpuBufferSlice uploadStaging(java.nio.ByteBuffer, long alignment, int usage);
  default GpuBufferSlice uploadStaging(java.util.List<java.nio.ByteBuffer>, long, int);
  default GpuBufferSlice uploadGpu(java.nio.ByteBuffer, long alignment, int usage);
  default GpuBufferSlice uploadGpu(java.util.List<java.nio.ByteBuffer>, long, int);
  java.util.List<GpuBufferSlice> multiUploadStaging(java.util.List<java.nio.ByteBuffer>, long, int);
  java.util.List<GpuBufferSlice> multiUploadGpu(java.util.List<java.nio.ByteBuffer>, long, int);
}
```

`GpuBuffer` usage flags, verified-by-javap: `USAGE_MAP_READ`, `USAGE_MAP_WRITE`,
`USAGE_HINT_CLIENT_STORAGE`, `USAGE_COPY_DST`, `USAGE_COPY_SRC`, `USAGE_VERTEX`, `USAGE_INDEX`,
`USAGE_UNIFORM`, `USAGE_UNIFORM_TEXEL_BUFFER`, `USAGE_INDIRECT_PARAMETERS`.
`GpuTexture` usage flags: `USAGE_COPY_DST`, `USAGE_COPY_SRC`, `USAGE_TEXTURE_BINDING`,
`USAGE_RENDER_ATTACHMENT`, `USAGE_CUBEMAP_COMPATIBLE`.

`GpuDevice.createTexture` requires a `com.mojang.blaze3d.GpuFormat` (not an int GL enum) —
`createTexture(Supplier<String> label, int usage, GpuFormat format, int width, int height, int depthOrLayers, int mipLevels)`,
plus a `String`-label overload. Confidence: `verified-by-javap`.

---

## 13. `OrderedSubmitNodeCollector` / `SubmitNodeCollector` (the `MultiBufferSource` successor)

Verified-by-javap.

```java
public interface SubmitNodeCollector extends OrderedSubmitNodeCollector {
  OrderedSubmitNodeCollector order(int order);
}

public interface OrderedSubmitNodeCollector {
  void submitShadow(PoseStack, float, java.util.List<EntityRenderState.ShadowPiece>);
  void submitNameTag(PoseStack, net.minecraft.world.phys.Vec3, int, net.minecraft.network.chat.Component,
                     boolean, int, net.minecraft.client.renderer.state.level.CameraRenderState);
  void submitText(PoseStack, float x, float y, net.minecraft.util.FormattedCharSequence text, boolean dropShadow,
                  net.minecraft.client.gui.Font.DisplayMode, int lightCoords, int color,
                  int backgroundColor, int outlineColor);
  void submitFlame(PoseStack, EntityRenderState, org.joml.Quaternionf);
  void submitLeash(PoseStack, EntityRenderState.LeashState);
  <S> void submitModel(net.minecraft.client.model.Model<? super S>, S, PoseStack,
                       net.minecraft.client.renderer.rendertype.RenderType, int, int, int,
                       net.minecraft.client.renderer.texture.TextureAtlasSprite, int,
                       net.minecraft.client.renderer.feature.ModelFeatureRenderer.CrumblingOverlay);
  // + default overloads taking Identifier / SpriteId / SpriteGetter
  void submitModelPart(net.minecraft.client.model.geom.ModelPart, PoseStack, RenderType, int, int,
                       TextureAtlasSprite /*, int, CrumblingOverlay, int*/);   // default overloads
  void submitMovingBlock(PoseStack, net.minecraft.client.renderer.block.MovingBlockRenderState, int);
  void submitBlockModel(PoseStack, RenderType, java.util.List<BlockStateModelPart>, int[], int, int, int);
  void submitBreakingBlockModel(PoseStack, java.util.List<BlockStateModelPart>, int);
  void submitShapeOutline(PoseStack, net.minecraft.world.phys.shapes.VoxelShape, RenderType, int, float, boolean);
  void submitItem(PoseStack, net.minecraft.world.item.ItemDisplayContext, int, int, int, int[],
                  java.util.List<net.minecraft.client.resources.model.geometry.BakedQuad>,
                  net.minecraft.client.renderer.item.ItemStackRenderState.FoilType);
  void submitCustomGeometry(PoseStack, RenderType, SubmitNodeCollector.CustomGeometryRenderer);
  void submitQuadParticleGroup(QuadParticleRenderState);
  void submitGizmoPrimitives(net.minecraft.client.renderer.gizmos.DrawableGizmoPrimitives.Group,
                             CameraRenderState, boolean);
}
```

`SubmitNodeStorage` is the concrete implementation (`net.minecraft.client.renderer.SubmitNodeStorage`),
with `order(int)`, `getSubmitsPerOrder()`, `drainPhases(Consumer<FeatureRenderPhase<?>>)`.

`submitCustomGeometry` is the escape hatch that most closely matches the old
`MultiBufferSource.getBuffer(RenderType)` + write-vertices flow: you supply a
`SubmitNodeCollector.CustomGeometryRenderer` and vanilla handles batching. Confidence:
`verified-by-javap` for the signature; the "escape hatch" characterization is `inferred`.

`EntityRenderState` no longer holds a `PoseStack`; it is a flat data record
(`x, y, z, ageInTicks, lightCoords, outlineColor, nameTag, shadowPieces, …`), and the pose is passed
separately to `submit(...)`. Confidence: `verified-by-javap`.

---

## 14. Uniforms and bind groups

### `BindGroupLayout` — verified-by-javap

```java
public class com.mojang.blaze3d.pipeline.BindGroupLayout {
  public static BindGroupLayout.Builder builder();
  public java.util.List<String> getSamplers();
  public java.util.List<BindGroupLayout.UniformDescription> getUniforms();
  public static java.util.List<String> flattenSamplers(java.util.List<BindGroupLayout>);
  public static java.util.List<BindGroupLayout.UniformDescription> flattenUniforms(java.util.List<BindGroupLayout>);
  public static void ensureCompatible(java.util.List<BindGroupLayout>);

  public static class Builder {
    public Builder withSampler(String name);
    public Builder withUniform(String name, com.mojang.blaze3d.shaders.UniformType);
    public Builder withUniform(String name, com.mojang.blaze3d.shaders.UniformType, com.mojang.blaze3d.GpuFormat);
    public BindGroupLayout build();
  }
}

public enum com.mojang.blaze3d.shaders.UniformType { UNIFORM_BUFFER, TEXEL_BUFFER }
```

There is **no** `BindGroupLayouts` class in `com.mojang.blaze3d`. The name the task asked about lives
at `net.minecraft.client.renderer.BindGroupLayouts` — verified-by-javap, public static final fields:

```java
DYNAMIC_TRANSFORMS, PROJECTION, MATRICES_PROJECTION, CHUNK_SECTION, FOG, GLOBALS, LIGHTING,
SAMPLER0, SAMPLER1, SAMPLER2, SAMPLER0_SAMPLER2, SAMPLER0_SAMPLER1, SAMPLER0_SAMPLER1_SAMPLER2,
CLOUD_INFO, DISSOLVE_MASK_SAMPLER, IN_SAMPLER, LIGHTMAP_INFO, SPRITE_ANIMATION_INFO, SPRITE,
CURRENT_SPRITE_NEXT_SPRITE
```

Bind group **order matters** and is asserted by `ensureCompatible`. `WorldMeshes` shows the correct
approach for reusing a vanilla layout: iterate `RenderPipelines.LINES.getBindGroupLayouts()` and pass
each one to `builder.withBindGroupLayout(layout)` (`verified-by-port`). `FullScreenPass` does the same
with `RenderPipelines.GUI_TEXTURED.getBindGroupLayouts()`.

### The default uniforms every vanilla-compatible pipeline expects

`RenderSystem.bindDefaultUniforms(RenderPass)` — verified-by-javap — binds the standard set in one
call. `GpuMeshRenderer` calls it before setting anything else. The names that appear in this repo's
correct code are `"DynamicTransforms"`, `"Projection"`, `"Fog"`, `"Globals"`/`"Lighting"`.

### `DynamicUniforms` — verified-by-javap

```java
public class net.minecraft.client.renderer.DynamicUniforms implements AutoCloseable {
  public static final int TRANSFORM_UBO_SIZE;
  public static final int CHUNK_SECTION_UBO_SIZE;
  public void reset();
  public com.mojang.blaze3d.buffers.GpuBufferSlice writeTransform(org.joml.Matrix4f);
  public com.mojang.blaze3d.buffers.GpuBufferSlice writeTransform(org.joml.Matrix4f, org.joml.Vector4f color);
  public com.mojang.blaze3d.buffers.GpuBufferSlice writeTransform(org.joml.Matrix4f, org.joml.Matrix4f);
  public com.mojang.blaze3d.buffers.GpuBufferSlice writeTransform(org.joml.Matrix4f, org.joml.Vector4f,
                                                                  org.joml.Vector3f, org.joml.Matrix4f);
  public com.mojang.blaze3d.buffers.GpuBufferSlice writeTransform(DynamicUniforms.Transform);
  public com.mojang.blaze3d.buffers.GpuBufferSlice[] writeTransforms(DynamicUniforms.Transform...);
  public com.mojang.blaze3d.buffers.GpuBufferSlice[] writeChunkSections(DynamicUniforms.ChunkSectionInfo...);
  public void close();
}
```

Reached via `RenderSystem.getDynamicUniforms()`. The `(Matrix4f, Vector4f)` overload is the
replacement for `RenderSystem.setShaderColor(r, g, b, a)` (which is gone): write the colour into
`DynamicTransforms` instead.

### `GlobalSettingsUniform` — verified-by-javap

```java
public class net.minecraft.client.renderer.GlobalSettingsUniform implements AutoCloseable {
  public static final int UBO_SIZE;
  public void update(int, int, double, long, net.minecraft.client.DeltaTracker, int,
                     net.minecraft.world.phys.Vec3, boolean);
  public void close();
}
```

`RenderSystem.setGlobalSettingsUniform(GpuBuffer)` / `getGlobalSettingsUniform()` (verified-by-javap)
install/fetch it; `bindDefaultUniforms` covers it for normal pipelines.

### Arbitrary named uniforms — how the repo solved it

Because `Uniform` is now an empty interface (`verified-by-javap`, §6) there is no per-name setter.
The repo's established pattern is: declare **one** UBO block for your shader's parameters, keep the
values in CPU-side records, and upload the packed block per draw.

`GlUniform.java` documents this explicitly:

> *"Minecraft 26.2 removed the immediate uniform API (`Uniform` is now an empty marker interface), so
> values are collected here and handed to the pipeline as a uniform buffer at draw time. Every
> uniform occupies one padded `vec4` slot of the shader's `PARAMETERS` block."*

`WorldMsdfDraw` is the worked example (`verified-by-port`): a 32-byte `MsdfParameters` buffer, four
floats per slot, declared on the pipeline with
`BindGroupLayout.builder().withUniform("MsdfParameters", UniformType.UNIFORM_BUFFER)` and bound with
`pass.setUniform("MsdfParameters", slice)` inside `GpuMeshRenderer`.

**Shader-side consequence:** every uniform you used to set by name must be redeclared in the `.fsh`/`.vsh`
inside that block (`layout(std140) uniform Parameters { vec4 uOffset; vec4 uHalfPixel; ... };`) and read
as `uOffset.xy` etc. This is a source change in `src/main/resources/assets/wyvern/shaders/**`, not only
a Java change.

---

## 15. Where shader identifiers / keys live now

| Concern | 26.2 answer | Confidence |
|---|---|---|
| Naming a shader | `net.minecraft.resources.Identifier` with path `core/<name>` under namespace `minecraft`, or your own namespace | verified-by-javap + verified-by-port |
| Attaching shaders to a draw | `RenderPipeline.Builder.withVertexShader(Identifier)` / `.withFragmentShader(Identifier)` | verified-by-javap |
| Naming a whole pipeline | `RenderPipeline.Builder.withLocation(Identifier)`; retrieve with `RenderPipeline.getLocation()` | verified-by-javap |
| Vanilla pipeline lookup by id | `RenderPipelines.PIPELINES_BY_LOCATION` exists but is `private static final` | verified-by-javap |
| Shader file location | `assets/<ns>/shaders/core/<name>.vsh` / `.fsh` (unchanged); `ShaderManager.SHADER_PATH` is a public constant | verified-by-javap |
| Post-processing chains | `ShaderManager.getPostChain(Identifier, Set<Identifier>)` — the `getProgram` path is gone | verified-by-javap |
| Shader defines | `RenderPipeline.Builder.withShaderDefine(String[, int\|float])`; `ShaderDefines` at `net.minecraft.client.renderer.ShaderDefines` | verified-by-javap |
| Precompiling | `GpuDevice.precompilePipeline(RenderPipeline)` → `CompiledRenderPipeline` (`isValid()` only) | verified-by-javap |

---

## 16. How fog state is expressed now

Summarised from §8. Data flow, all `verified-by-javap`:

```
FogRenderer.setupFog(camera, renderDistance, deltaTracker, partialTick, level) -> FogData
FogRenderer.updateBuffer(FogData)
FogRenderer.getBuffer(FogRenderer.FogMode) -> GpuBufferSlice
RenderSystem.setShaderFog(GpuBufferSlice)
   -> pipeline binds BindGroupLayouts.FOG and pass.setUniform("Fog", slice)
```

`FogData` is a mutable holder of plain public floats plus `public Vector4f color`. There is no
`FogParameters` value object. The camera's current fog is also published on
`CameraRenderState.fogData` / `CameraRenderState.fogType`. `FogRenderer.toggleFog()` is a public
static toggle; `FogRenderer.endFrame()` must be called once per frame by whoever drives it
(normally the level renderer).

`STATUS.md` says effect fog disabling is already handled through `MobEffectFogEnvironment`; the
abstract base is `net.minecraft.client.renderer.fog.environment.FogEnvironment` — that base class was
**not** javap-verified here (`inferred`).

---

## 17. How block rendering dispatch works now

Summarised from §9, all `verified-by-javap`:

* Resolve: `new BlockModelResolver(ModelManager)` → `update(BlockModelRenderState, BlockState, BlockDisplayContext.create())`.
* Submit: `BlockModelRenderState.submit(PoseStack, SubmitNodeCollector, int light, int overlay, int outline)`.
* Low-level tessellation: `new ModelBlockRenderer(ambientOcclusion, cull, BlockColors).tesselateBlock(BlockQuadOutput, x, y, z, BlockAndTintGetter, BlockPos, BlockState, BlockStateModel, long seed)`, sourcing the model from `BlockStateModelSet.get(BlockState)`.
* Quad sink: `interface BlockQuadOutput { void put(float x, float y, float z, BakedQuad quad, QuadInstance instance); }`.
* There is **no** `BlockRenderDispatcher` class and **no** `renderSingleBlock(...)`.

---

## 18. Text: `Font.drawInBatch` is gone

Relevant to `CrystalAura.java` (line ~1241) and `TotemPop.java`. `verified-by-javap`:

```java
public interface net.minecraft.client.gui.Font.PreparedText {
  void visit(Font.GlyphVisitor);
  net.minecraft.client.gui.navigation.ScreenRectangle bounds();
}
// Font
public Font.PreparedText prepareText(...);
public Font.PreparedText prepare8xTextOutline(...);
```

`Font.drawInBatch(...)` is absent. For world text, the supported path is
`OrderedSubmitNodeCollector.submitText(PoseStack, float, float, FormattedCharSequence, boolean,
Font.DisplayMode, int light, int color, int backgroundColor, int outlineColor)` (verified-by-javap;
for this repo's MSDF world font, `WorldMsdfDraw` already bypasses `Font` entirely and draws its own
geometry — verified-by-port).

---

## 19. Per-file notes for the 12 files

| File | Blocking symbols | Route |
|---|---|---|
| `...\utility\render\shader\ShaderHandsRenderer.java` | `GlProgram`, `findUniform`/`GlUniform`, `BufferUploader` (already partly ported) | Build one `RenderPipeline` per pass; pack uniforms into a `PARAMETERS` UBO; draw via `MeshBuilder` + `GpuMeshRenderer`. `GetCustomShaderKey` substitution point is unresolved — see below. |
| `...\utility\render\shader\HandShaderRenderer.java` | `BufferUploader` | same mechanical conversion |
| `...\utility\render\display\shader\GlProgram.java` | `CompiledShaderProgram`, `RenderStateShard`, `ShaderProgram`, `ShaderManager.CompilationException`, `getProgramForLoading`, `RenderSystem.setShader`, `ShaderProgramAccessor` | Rewrite as a pipeline holder: `Identifier`s + `VertexFormat` + optional `PARAMETERS` block. Delete `renderPhaseProgram()` and `use()`. |
| `...\utility\render\display\shader\DrawUtil.java` | ~20× `BufferUploader.drawWithShader`, `CoreShaders.POSITION_COLOR`/`POSITION_TEX_COLOR`, `setShaderTexture`, blend/cull/lineWidth, `mc.getMainRenderTarget()`, `TextureTarget`, `blitToScreen`, `bindRead/bindWrite` | Convert every draw to a cached `RenderPipeline` (see `WorldMeshes`) or a `FullScreenPass`-style helper. Main-target and blit sites map as in §11. |
| `...\utility\render\display\Render2DUtil.java` | same as `DrawUtil` | same |
| `...\client\modules\impl\render\TotemPop.java` | `mc.renderBuffers().bufferSource()`, `dispatcher.render(...)`, `endBatch()` | extract/submit (§3a); if no collector is available, rebuild the entity geometry with `MeshBuilder` + `GpuMeshRenderer`. |
| `...\client\modules\impl\render\TargetESP.java` | 10× `CoreShaders`, `BufferUploader` | `WorldMeshes`-style pipelines |
| `...\client\modules\impl\render\Satan.java` | 17× `CoreShaders`, 10× `RenderSystem.blendFunc(...)` | pipelines + `BlendFunction` (§10) |
| `...\client\modules\impl\render\Cosmetics.java` | `CoreShaders`, `MultiBufferSource` parameter, `BufferUploader`, `RenderSystem.blendFunc(GL11...)`, `RenderSystem.setShaderColor` | parameter type → `SubmitNodeCollector`; blend → `BlendFunction`; `setShaderColor` → vertex colour or `DynamicUniforms.writeTransform(Matrix4f, Vector4f)` |
| `...\utility\mixin\client\render\RenderSystemMixin.java` | `RenderSystem.setShader(ShaderProgramKey)` — target gone | **unresolved**, see §20 |
| `...\utility\mixin\accessors\ShaderProgramAccessor.java` | `CompiledShaderProgram.getUniformsByName()` — no equivalent | **delete the accessor**, see §20 |
| `...\client\modules\impl\combat\CrystalAura.java` | `CoreShaders.POSITION_COLOR`, `mc.renderBuffers().bufferSource()`, `mc.font.drawInBatch(...)`, `endBatch()` | pipelines; text → `submitText` or the MSDF path |

---

## 20. NOT RESOLVED — read this before guessing

1. **`RenderSystemMixin` has no target.**
   `RenderSystem.setShader(ShaderProgramKey)` does not exist in 26.2, so the mixin's descriptor is
   stale and the injection cannot apply. Exhaustive search found **no** `setShader` method of any
   shape on `RenderSystem` (verified-by-javap). The two *real* methods that could host an equivalent
   hook, both verified-by-javap, are:
   * `net.minecraft.client.renderer.rendertype.RenderType.pipeline()` — the only place the hand
     item's pipeline is chosen at draw time (`RenderType` itself verified to expose `pipeline()`).
   * `net.minecraft.client.renderer.ItemInHandRenderer.submitHandsWithItems(float, PoseStack, SubmitNodeCollector, LocalPlayer, int)`
     — where hands are queued.
   `ShaderHandsRenderer` carries a `TODO(26.2)` noting that the draw-time lookup happens after the
   `renderingHands` flag has been reset, so a naive flag-based hook into `RenderType.pipeline()` will
   not work either. **The correct substitution point has not been found.** Do not invent one.
   `RenderPipelines.*` constants are `public static final` with no setter, so they cannot be rewritten.

2. **`ShaderProgramAccessor` cannot be repaired.**
   It targets `CompiledShaderProgram.getUniformsByName()`. `CompiledShaderProgram` is gone, and its
   only successor, `CompiledRenderPipeline`, exposes nothing but `isValid()` (verified-by-javap).
   There is no reflection or accessor path to a uniforms map. The accessor must be **deleted**, and
   every `findUniform` caller rewritten around UBO blocks (§14).

3. **`Uniform`'s setter API is gone.**
   `com.mojang.blaze3d.opengl.Uniform` is now an empty marker interface with only
   `default void close()` (verified-by-javap). Whether any implementation with setters exists in the
   jar was not found. Treat per-name uniform writes as impossible.

4. **No public way to obtain a `SubmitNodeCollector`.**
   `SubmitNodeStorage` is the only implementation and is constructed by the level renderer. Whether a
   mod can get one during a Fabric `WorldRenderEvents` callback is **unknown**. Until this is resolved,
   prefer building your own `MeshData` and drawing it with `GpuMeshRenderer`.

5. **`BlendFunction.ADDITIVE` vs `new BlendFunction(BlendFactor.SRC_ALPHA, BlendFactor.ONE)`.**
   Both compile; the repo uses the explicit constructor. Whether the constant has identical record
   components was not checked. Prefer the explicit form.

6. **`FogEnvironment` API not javap-verified.** Only reported by `STATUS.md`. The concrete members of
   `net.minecraft.client.renderer.fog.environment.FogEnvironment` are unverified.

7. **`RenderSystem.setShaderFog(Matrix4f)` is gone.** Only the `GpuBufferSlice` overload survives
   (verified-by-javap). Any pre-existing code that computed a fog matrix and pushed it directly must
   be rerouted through `FogRenderer.setupFog` → `updateBuffer` → `getBuffer` → `setShaderFog(GpuBufferSlice)`.
   No call site of the old form was found in this repo, so this is a heads-up rather than a live task.

8. **Stale audit rows.** `migration\26.2\compatibility-audit.md` lists 1 file each for
   `FogParameters` and `BlockRenderDispatcher`; repo-wide grep found no current usage. Do not spend
   time on those two rows.

---

## 21. Things that were checked and are *still present* (do not migrate)

`RenderSystem` (at `com.mojang.blaze3d.systems.RenderSystem`) — verified-by-javap, retains:
`getDevice()`, `tryGetDevice()`, `assertOnRenderThread()`, `isOnRenderThread()`, `getDynamicUniforms()`,
`bindDefaultUniforms(RenderPass)`, `getModelViewMatrixCopy()`, `getModelViewStack()`,
`getSequentialBuffer(PrimitiveTopology)`, `getProjectionMatrixBuffer()`,
`setProjectionMatrix(GpuBufferSlice, ProjectionType)`, `getProjectionType()`, `backupProjectionMatrix()`,
`restoreProjectionMatrix()`, `getSamplerCache()`, `setShaderFog/getShaderFog`, `setShaderLights/getShaderLights`,
`setGlobalSettingsUniform/getGlobalSettingsUniform`, `enableScissorForRenderTypeDraws(int,int,int,int)`,
`disableScissorForRenderTypeDraws()`, `getScissorStateForRenderTypeDraws()`, `queueFencedTask(Runnable)`,
`public static GpuTextureView outputColorTextureOverride;`, `public static GpuTextureView outputDepthTextureOverride;`.

Also present: `com.mojang.blaze3d.PrimitiveTopology` (LINES, DEBUG_LINES, DEBUG_LINE_STRIP, POINTS,
TRIANGLES, TRIANGLE_STRIP, TRIANGLE_FAN, QUADS), `com.mojang.blaze3d.IndexType` (SHORT, INT with
`public final int bytes`), `com.mojang.blaze3d.pipeline.RenderTarget`, `TextureTarget`, `MappableRingBuffer`,
`RenderPipelines`, `RenderTypes`, `net.minecraft.client.renderer.rendertype.RenderType`,
`net.minecraft.client.renderer.texture.TextureManager.getTexture(Identifier)` →
`AbstractTexture` with `getTexture()`, `getTextureView()`, `getSampler()`,
`net.minecraft.client.gui.render.TextureSetup` (`singleTexture`, `singleTextureWithLightmap`,
`doubleTexture`, `noTexture`), and `Minecraft.gameRenderer.mainCamera()` / `.mainRenderTarget()`.
