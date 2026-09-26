# Перенос клиента на Minecraft 26.2

Перенос не завершён. Рабочая копия находится здесь; основной проект и последний готовый JAR остаются на Minecraft 1.21.4. Готового JAR для 26.2 пока нет.

Подготовлены Java 25, Gradle 9.5.1, Loom 1.17.21, Fabric Loader 0.19.5 и Fabric API 0.161.0+26.2. Исходники переведены с Yarn на официальные имена Minecraft. Обновлены зависимости, манифест, Identifier, ContainerInput и перемещённые классы.

Адаптированы:

- Экраны MenuScreen, HudEditorScreen, LoginScreen и AltManagerScreen: extractRenderState и новые события KeyEvent, CharacterEvent, MouseButtonEvent.
- Gui/Hud: смена экранов и извлечение состояния HUD перенесены на новые владельцы. EventHudRender теперь вызывается из Hud.extractRenderState.
- CustomDrawContext использует композицию с GuiGraphicsExtractor и собственную PoseStack. Предметы, полоски прочности, кулдауны, текстуры, прямоугольники и скруглённая геометрия отправляются в отложенный GUI-рендер.
- Масштаб HUD применяется через его матрицу и размеры контекста. Глобальные поля масштаба Window больше не изменяются.
- MsdfGuiRenderer и новый шейдер msdf_gui сохраняют прежнюю раскладку глифов, цвета компонентов и градиенты. Геометрия сохраняется в неизменяемом GuiMeshState.
- Скругления и границы GUI используют геометрию с прозрачной каймой вместо старых немедленных GL-шейдеров. Внешний вид ещё нужно сверить в игре.
- Arrows использует отложенный вывод текстуры и новую камеру.
- KeyboardMixin/MouseMixin используют keyPress/onButton/onScroll. KeyboardInputMixin работает с keyPresses/moveVector и нормализацией диагонального движения. Обновлены чтения направления движения в модулях и сброс направления при смене элитры.
- FullBright использует LightmapRenderStateExtractor; переключение принудительно обновляет lightmap. Туман использует FogData, а отключение тумана эффектов — MobEffectFogEnvironment.
- Условия спринта и получение состояния воды/лавы переведены на доступные методы. SimulatedPlayer сохраняет собственные снимки высоты жидкости и жидкости у глаз.
- Проекция координат использует GameRenderer.projectPointToScreen; прямое чтение GL viewport удалено.
- MeshBuilder заменяет удалённый Tesselator. GpuMeshRenderer отправляет меши через CommandEncoder/RenderPass, использует временную память кадра и закрывает MeshData. Он подключён к MSDF для текста в мире; остальные старые вызовы BufferUploader ещё требуют переноса.
- TriggerBot использует теги оружия и новые методы инвентаря. AutoArmor использует Equippable. Броня HUD читается через EquipmentSlot.

Проверки 2026-09-18:

- Отдельная компиляция обновлённых обработчиков ввода, аксессоров, MeshBuilder, SprintConditions, GUI-контекста, геометрии, шрифтов и mixins освещения/тумана против реальных классов Minecraft 26.2 прошла. Использовались исходники адаптеров и существующие общие классы проекта; это не полная сборка приложения. Аннотационный процессор в этой отдельной проверке отключён; запуск Mixins она не подтверждает.
- Новый MSDF GUI-шейдер прошёл компиляцию и линковку на OpenGL-видеокарте для пяти значений диапазона атласа. Проверены блоки Projection/DynamicTransforms и Sampler0. Эта проверка не проверяет картинку в Minecraft и Vulkan.
- Последняя полная compileJava завершилась ошибкой: 93 ранние ошибки разрешения типов. После их исправления могут обнаружиться другие несовместимости API.
- Аудит реального JAR Minecraft обнаружил 11 отсутствующих импортируемых классов и 1 несовместимую запись access widener из 47: старый RenderTarget.depthBufferId. Подробности находятся в compatibility-audit.md.
- Запуск клиента на 26.2 и проверка в игре не проводились.

Остаётся перенести старые DrawUtil/GlProgram, оставшиеся вызовы BufferUploader, MultiBufferSource, шейдеры мира/рук, framebuffer/stencil и изменённые точки внедрения рендерных Mixins. Также требуется полная проверка методов сущностей, пакетов и остальных Mixins, затем успешная сборка и запуск клиента. Функции не следует отключать ради формального прохождения компиляции.

LonyGrief сохранена в этой копии: источник Downloads/wyvern-dlc-ready.rar, обновление в EventGameUpdate (240 Гц), проверка атак по фактическому углу игрока. Основная сборка 1.21.4 с этим исправлением прошла build; ротация в игре не проверена.

Отдельная проверка CrystallAura: логика основного проекта совпадает с Downloads/wyvern-dlc.rar после исключения импортов, пустых строк и аннотаций FastNative (1125 строк в обоих файлах). Файлы архива не исполнялись.

Официальная информация: https://www.fabricmc.net/2026/06/15/262.html
Дополнительные изменения 2026-09-18:

- MSDF для текста в мире переведён на GpuMeshRenderer/WorldMsdfDraw. Параметры атласа и плавного затухания передаются через 32-байтовый блок MsdfParameters. Сохранены перегрузки renderText, цветные сегменты и градиенты.
- Шейдер msdf_world прошёл компиляцию и линковку на OpenGL-видеокарте, включая проверку размера блока MsdfParameters. Вывод в Minecraft и работа Vulkan ещё не проверены.
- CameraMixin адаптирован к alignWithEntity: базовые углы корректируются отдельно от разворота камеры спереди. Смена позиции теперь проходит через штатный setPosition, который обновляет внутреннее состояние камеры. Камера клип, FOV и AspectRatio перенесены на новые методы, включая проекцию отсечения.
- Событие рендера мира подключено после LevelRenderer.render; матрица вида берётся из его аргумента, вместо старых локальных переменных и поля renderHand.
- Новый GPU-код, MSDF для мира и CameraMixin отдельно компилируются против Minecraft 26.2. Порядок аргументов RenderPass.drawIndexed сверён с GuiRenderer самой игры: количество индексов, количество экземпляров, первый индекс, базовая вершина, первый экземпляр.
- Проекция глубины учитывает DeviceInfo.isZZeroToOne для разных графических backend.
- Полная сборка по-прежнему не проходит. Текущие 93 ошибки — ранние ошибки отсутствующих типов; число не описывает все оставшиеся работы. Новые точки внедрения Mixins при запуске ещё не проверены.

## Работа 2026-09-19 (остановлена по просьбе)

### Что сделано и проверено по коду

- **GlUniform.java (создан).** В 26.2 `com.mojang.blaze3d.opengl.Uniform` — пустой интерфейс-маркер (только `close()`), поэтому `findUniform(name).set(...)` невозможен. Добавлен собственный держатель значения: по одному дополненному `vec4` на униформу.
- **GlProgram.java (переписан).** Одна std140-блок-структура `WyvernParams`, по одному `vec4` на униформу в порядке конструктора; `uniformData()` отдаёт ровно `16 × n` байт. `ensureLoaded()`/`isLoaded()`/`pipeline()` заменяют загрузку `ShaderProgram`. `findUniform()` не возвращает null (пишет ошибку и отдаёт отделённый объект), `use()` очищает значения. Смешивание задано явно — `new BlendFunction(SRC_ALPHA, ONE_MINUS_SRC_ALPHA)` в `ColorTargetState`, с сохранением формата и write mask базового пайплайна; это замена удалённого `RenderSystem.defaultBlendFunc()`.
- **Исправлен дефект путей шейдеров в GlProgram.** Было `withVertexShader(this.location)` и `withFragmentShader(this.location)`, где `location` — это `wyvern:core/rectangle/data`. В 26.2 идентификатор разрешается прямо в `assets/wyvern/shaders/<path>.vsh`, то есть в несуществующий файл. Настоящие пути хранились только в старых `data.json`, и они не выводимы из id программы: `rectangle/data` рисуется общим `core/position_color`, `blur/data` — своим `core/blur/vertex`, все `hands/*` и `handstrail/*` — через `core/kawase_down/vertex`. Добавлена таблица из 27 программ, перенесённая из `data.json` (26.2 их больше не читает). Без этого все 2D-программы ссылались бы на отсутствующие шейдеры.
- **KawaseBlurProgram.java (переписан)** под новый GlProgram, 5 униформ. Класс нигде не создаётся — мёртвый код и в 26.2-копии.
- **CustomRenderTarget.java (переписан).** Привязки framebuffer в 26.2 нет: цель — пара `GpuTexture`, и проход рисует в неё через `RenderSystem.outputColorTextureOverride` / `outputDepthTextureOverride`, а очистка идёт через `CommandEncoder.clearColorTexture` / `clearColorAndDepthTextures`. Фильтрация — больше не свойство цели, а `GpuSampler`; добавлены `sampler()`, `textureSetup()`, `clear()`, `destroy()`. Удалён `setFilterMode(int)`. Исправлен мой же поздний NPE: конструктор по размеру вызывает `resize()`, который может записать размеры без выделения буферов, поэтому добавлена проверка `getColorTexture() == null`.
- **GpuMeshRenderer: добавлена перегрузка с модулятором цвета** (`writeTransform(modelView, Vector4f)`) — это замена удалённого `RenderSystem.setShaderColor(r, g, b, a)`.
- **wyvern.mixins.json**: убраны записи `accessors.ShaderProgramAccessor` и `client.render.RenderSystemMixin`.
- **Удалены два файла миксинов.** `ShaderProgramAccessor` — целевой класс `CompiledShaderProgram` больше не существует. `RenderSystemMixin` — `@ModifyVariable` на `RenderSystem.setShader(ShaderProgramKey)`, которого нет: это гарантированный отказ применения миксина при запуске, то есть хуже, чем отсутствие файла. Ссылок на оба не было.
- **wyvern.accesswidener**: удалена недействительная строка `accessible field com/mojang/blaze3d/pipeline/RenderTarget depthBufferId I` (у `RenderTarget` такого поля нет; класс теперь `abstract` с конструктором `(String, boolean, GpuFormat)`). Остальные 46 записей сверены.
- **API-MAP-26.2.md (создан агентом).** Сверенный через javap разбор удалённых классов и их замен, таблица по каждому файлу и раздел открытых вопросов §20.

### Установленные правила по шейдерам

- Имена `ColorModulator`, `ModelViewMat`, `ProjMat`, `ModelOffset`, `TextureMat` **нельзя** передавать в конструктор `GlProgram` и нельзя объявлять внутри `WyvernParams`. Подключаемые через `#moj_import` файлы `<minecraft:dynamictransforms.glsl>` и `<minecraft:projection.glsl>` объявляют безымянные блоки, а GLSL помещает члены безымянного блока в глобальную область видимости — повторное объявление является ошибкой компиляции. Для поведения это безопасно: Java нигде не задавала `ColorModulator`, всегда действовало значение 1,1,1,1 из `data.json`.
- Шейдеры `*_gpu` (`aurora_aurora_gpu`, `motion_blur_gpu`, `saturation_gpu`, `block_highlight_gpu`, `skyshader_*_gpu`, `sky_gpu`, `fullscreen_gpu`, `wet_world_gpu`) перенесены в прошлой сессии и используют другое, плотно упакованное соглашение о блоке. Их трогать не следует.

### Инструмент проверки GLSL

На машине есть рабочий валидатор: `.codex_tmp_migration/GuiShaderCheck.java` и список путей `.codex_tmp_migration/shader-check-classpath.txt`. Он создаёт реальный контекст OpenGL 3.3, читает настоящие `.vsh`/`.fsh`, подставляет `#moj_import <minecraft:…glsl>` из ванильного JAR и проверяет компиляцию, линковку, наличие блоков `DynamicTransforms`/`Projection`, `Sampler0` и смещения активных униформ. Планировалось расширить его до проверки наличия `WyvernParams`, размера `16 × n` и смещений по каждому GlProgram и прогнать по всем программам — **это сделано не было**.

### Состояние агентов

Запускались четыре фоновых агента. Три остановлены по просьбе пользователя, работу не завершили:

- `a82e72a362d4d6807` (DrawUtil, Render2DUtil) — остановлен перед записью правок. В `DrawUtil.java` остаётся разрыв компиляции: строки 161, 192, 225, 316 обращаются к `program.backingProgram` — поля в новом GlProgram нет, заменяется на `!program.isLoaded()`.
- `adb1ad2ce8feac9b3` (HandShaderRenderer, ShaderHandsRenderer, access widener) — остановлен в момент, когда нашёл ошибку импорта и не успел её исправить.
- `adde6035f6353d26e` (CrystalAura, Cosmetics, Satan, TargetESP, TotemPop) — остановлен на середине, частично.
- `a8c1d92364fa2c884` (карта API) — завершил работу, результат в API-MAP-26.2.md.

Два готовых сообщения агентам не были доставлены из-за временной недоступности классификатора безопасности: в них были разрыв с `backingProgram`, правило о повторном объявлении и таблица униформ.

### Не сделано

- Полная сборка не запускалась.
- Валидатор GLSL по всем программам не прогонялся.
- Клиент на 26.2 не запускался.
- Не решён вопрос с `SubmitNodeCollector`: публичного способа его получить нет, единственная реализация `SubmitNodeStorage` создаётся рендерером мира. Это затрагивает TotemPop, CrystalAura и Cosmetics.
- Не сверены компоненты `BlendFunction.ADDITIVE` и новый конструктор `TextureTarget` из 5 аргументов.

Ограничение из предыдущей записи остаётся в силе: функции не отключаются ради формального прохождения компиляции.

## Работа 2026-09-19 (продолжение)

### Шейдеры

- Переведены на `#version 330` десять живых программ: `core/kawase_down/vertex.vsh`, `core/kawase_up/vertex.vsh` (общий вершинный шейдер для всех `hands/*` и `handstrail/*`), `core/kawase_down/fragment.fsh`, `core/kawase_up/fragment.fsh`, `core/msdf_font/vertex.vsh`, `core/msdf_font/fragment.fsh`, `core/hands/hands_mask_diff.fsh`, `core/saturation/saturation.fsh`, `core/motion_blur/motion_blur.vsh`, `core/motion_blur/motion_blur.fsh`.
- В каждом фрагментном шейдере одна std140-структура `WyvernParams`, все члены `vec4` и в порядке конструктора `GlProgram`. Бывшие `bool`-униформы стали `vec4` и читаются через `.x != 0.0`. Выходная переменная переименована в `out vec4 OutColor;`.
- Проверено поиском: одиннадцать оставшихся файлов с `#version 150` (`block_highlight`, `aurora/aurora`, `wet_world/fragment`, `sky/sky_shader.vsh|fsh`, `skyshader/*`) мертвы — у каждой живой программы есть парный `*_gpu`, который и используется.

### Java

- **DrawUtil.java дописан.** Разрыв с `program.backingProgram` (строки 161, 192, 225, 316 из прошлой записи) закрыт. `drawBlur` переписан: копия экрана в offscreen-цель вместо blit, затем `GpuMeshRenderer.draw(...)`. Доступ к пайплайнам сведён к делегированию в `VanillaPipelines`; в классе осталось одно поле `textureOnly`.
- **VanillaPipelines.java.** Исправлено имя ванильного шейдера: `core/position_tex_color` (было `core/position_texture_color`, это копия в пространстве имён wyvern, а не ванильный ресурс).
- **Cosmetics.java закрыт.** Все немедленные GL-состояния убраны, каждый вызов идёт через `WorldMeshes.draw(mesh, texture, additive, depth)`. Аддитивность и глубина стали флагами пайплайна; линии (обводки и «рёбра» крыльев) собираются как `PrimitiveTopology.LINES` с `POSITION_COLOR_NORMAL_LINE_WIDTH` и шириной на вершину.
- **CrystalAura.java закрыт.** `drawActionBox` рисует через `WorldMeshes.draw(..., null, false, false)` (`depth = false` — это отсутствие теста глубины, как старый `disableDepthTest`). `drawDamageText` переведён на мировой MSDF-текст `MsdfRenderer.renderText(Fonts.SEMIBOLD, ...)`: в 26.2 из `EventRender3D` пакета для отрисовки ванильного шрифта нет, а пайплайн MSDF-текста идёт без теста глубины, что совпадает со старым `SEE_THROUGH`. Масштаб и центрирование сохранены константами `DAMAGE_TEXT_SCALE` / `DAMAGE_TEXT_SIZE`.
- **StencilUtil.java удалён.** В 26.2 трафаретного состояния не осталось вовсе, а класс опирался на `mc.getMainRenderTarget()`, `depthBufferId` и `bindWrite`. Единственная точка вызова — область прокрутки ClickGUI в `ClickGuiRenderer` — заменена на отсечение ножницами через экстрактор: `context.enableScissor(...)` / `disableScissor()`. Раньше первым делом рисовался скруглённый прямоугольник-маска; видимым он не был (шёл под `colorMask(false)`), а теперь это отложенная GUI-геометрия, на которую то состояние уже не действует, поэтому он убран. Отличие только в форме границы отсечения: прямоугольная вместо скругления 6px. В `ClickGuiSettingRenderer` такое же отсечение уже использовалось.
- Удалён устаревший импорт `StencilUtil` в `ClickGuiSettingRenderer` и `ClickGuiRenderer`.

### Осталось (блокирует сборка)

- **TotemPop.java и LivingEntityRendererMixin.java.** В 26.2 `EntityRenderDispatcher` больше не имеет `render(...)`: рендер разделён на `extractEntity` и `submit(..., PoseStack, SubmitNodeCollector)`. Поэтому TotemPop не может отрисовать призрак из `EventRender3D`, а два `@Redirect` в `LivingEntityRendererMixin` нацелены на удалённые `MatrixStack`/`VertexConsumerProvider`. Правильная замена — внедряться туда, где коллектор существует (окно `EntityRenderDispatcher.submit`). Точные дескрипторы этих методов ещё не сверены: `javap` по JAR 26.2 в этой сессии недоступен из-за недоступности классификатора безопасности. Придумывать дескрипторы нельзя — неверный дескриптор означает молча не применившийся миксин.
- Валидатор GLSL по всем программам не прогонялся.
- Полная сборка не запускалась.

## Работа 2026-09-19 (сборка впервые запущена)

### Инфраструктура: сборка не запускалась из-за отсутствия JDK 25

Первый запуск `compileJava` упал не на коде: `Cannot find a Java installation ... matching: {languageVersion=25}`. На машине стоят только JDK 17 и 21. JDK 25 (Temurin 25.0.4.1+1) уже был скачан в `.tools/java25/jdk-25.0.4.1+1` в корне рабочей области, но Gradle его не находил.

- В `gradle.properties` добавлено `org.gradle.java.installations.paths=C:/Users/Karitsa/Desktop/wyvern-dlc/.tools/java25/jdk-25.0.4.1+1`. Отсутствующие пути Gradle игнорирует, поэтому на другой машине это безвредно. Альтернатива, если путь переедет: `JAVA_HOME=<jdk25> ./gradlew build` — тогда ветка `toolchain.languageVersion` в `build.gradle` вообще не выполняется.

После этого **сборка впервые реально компилирует код**: 322 ошибки, все — обычные ошибки типов, а не отказ инструментов. Это длинный хвост механических правок, а не архитектурные блокеры.

### Аудит миксинов

Все 42 целевых класса `@Mixin` проверены на наличие в JAR 26.2 — отсутствующих нет. `ClientLevelData` (миксин `ClientWorldPropertiesMixin`) существует как вложенный класс `net.minecraft.client.multiplayer.ClientLevel$ClientLevelData`. Поскольку конфиг `required: true`, это была реальная угроза падения при загрузке; её нет.

### Сверено через javap (снимает пункты «не проверено»)

- `TextureTarget(String, int, int, boolean, GpuFormat)` — 5 аргументов, подтверждено. `CustomRenderTarget` наследует `RenderTarget(String, boolean, GpuFormat)`; `GpuFormat.RGBA8_UNORM` существует.
- `BlendFunction.ADDITIVE` — не существует; аддитивность везде `new BlendFunction(SRC_ALPHA, ONE)`. Пункт закрыт.
- `EntityRenderDispatcher`: `extractEntity(E, float)` и `submit(S, CameraRenderState, double, double, double, PoseStack, SubmitNodeCollector)`. Метода `render(...)` нет.
- `LevelRenderState.cameraRenderState` — публичное поле.
- `LivingEntityRenderer` в 26.2 вообще не имеет `render(...)`; есть только `submit`, `extractRenderState`, `getRenderType`.

### Главные причины ошибок (по убыванию)

- 94× `handleInventoryMouseClick(int,int,int,ContainerInput,LocalPlayer)` — метода нет. Замена: `handleContainerInput(int, int, int, ContainerInput, Player)` — та же арность и порядок, имя изменилось, последний параметр расширен с `LocalPlayer` до `Player`.
- 78× `selected has private access in Inventory` — закрыто одной строкой в `wyvern.accesswidener` (`accessible` + `mutable` для `Inventory.selected`), а не переписыванием 78 мест вызова на `getSelectedSlot()`.
- 20× `InputConstants.isKeyDown(Window, int)` — теперь принимает `Window`, а не `long`: `mc.getWindow().handle()` → `mc.getWindow()`. Сам `Window.handle()` жив и по-прежнему возвращает `long`.
- `RenderSystem` полностью лишился `depthMask`, `enableBlend`, `disableBlend`, `blendFunc`, `defaultBlendFunc`, `setShaderColor`, `lineWidth`, `enableCull`, `disableCull`, `setShader`, `setShaderTexture`, `getMainRenderTarget`.
- `MobEffects.DIG_SPEED` → `HASTE`, `DAMAGE_RESISTANCE` → `RESISTANCE`; оба теперь `Holder<MobEffect>`, а не `MobEffect`.
- `InputConstants.PRESS_SHIFT_KEY` / `RELEASE_SHIFT_KEY` удалены; остались `KEY_LSHIFT`, `KEY_RSHIFT`, `MOD_SHIFT`.
- `Minecraft.hideGui` и `Minecraft.cameraEntity` отсутствуют.

### Среды выполнения

- `DrawUtil.java` — шесть ошибок `cannot find symbol: VanillaPipelines` были отсутствующим импортом; добавлен `import wtf.wyvern.utility.render.VanillaPipelines;`. Все шесть вызываемых методов (`color`, `textured`, `of`, `lines`, `texture`, `screenSampler`) в классе есть с нужными сигнатурами.
- `Keyboard.java` — `isKeyDown` переведён на `Window`.
- Миксин призрака тотема закрыт двумя агентами: `TotemPop.submitGhosts(...)` вызывается из нового `@Inject` TAIL на `LevelRenderer.submitEntities(PoseStack, LevelRenderState, SubmitNodeCollector)` в уже существующем `WorldRendererMixin`; `LivingEntityRendererMixin` переведён на `submit(...)` с `@Redirect` на `getRenderType` и `@ModifyArgs` на `SubmitNodeCollector.submitModel(...)`. Дескрипторы подтверждены `javap -s`, вызов `submitModel` — дизассемблированием `LivingEntityRenderer.submit`; призрачные `light = 0xF000F0` и `overlay = 0x100010` сохранены через аргументы 4 и 5.

## Работа 2026-09-19 (продолжение: 322 → 74 ошибки)

### Итог по числам

Ошибок компиляции: **322 → 74**. Сборка запускается и компилирует код. Клиент на 26.2 по-прежнему не запускался.

### Аудит миксинов: три отдельных проверки

Миксин-конфиг имеет `required: true` и `injectors.defaultRequire: 1`, поэтому любая неразрешённая цель роняет игру при загрузке — и **компилятор этого не видит**. Проверено три независимых слоя:

1. **Целевые классы `@Mixin`.** Все 42 сверены с JAR 26.2 — отсутствующих нет.
2. **Записи `wyvern.mixins.json`.** Все 49 записей указывают на существующие `.java`. (Смежные записи `client.HandledScreenMixin` и `client.render.gui.screen.HandledScreenMixin` — два разных класса, оба на месте.)
3. **Строки-дескрипторы `method = "..."`.** Здесь и нашлись настоящие дефекты. Извлечены все строки методов; обнаружены **пять** со старыми Yarn-именами классов, которые не могли разрешиться, потому что рантайм на официальных именах:

| Файл | Было | Стало |
|---|---|---|
| `client/EntityMixin.java` | `move(Lnet/minecraft/entity/MovementType;Lnet/minecraft/util/math/Vec3d;)V` | `move(Lnet/minecraft/world/entity/MoverType;Lnet/minecraft/world/phys/Vec3;)V` |
| `client/EntityMixin.java` | `@At` target `Entity.isControlledByClient()Z` | `Entity.isLocalInstanceAuthoritative()Z` |
| `minecraft/network/ClientConnectionMixin.java` | `send(Lnet/minecraft/network/packet/Packet;)V` | `send(Lnet/minecraft/network/protocol/Packet;)V` |
| `minecraft/team/TeamMixin.java` | `decorateName(Lnet/minecraft/text/Text;)Lnet/minecraft/text/MutableText;` | `getFormattedName(Lnet/minecraft/network/chat/Component;)Lnet/minecraft/network/chat/MutableText;`-эквивалент: `...(Component;)Lnet/minecraft/network/chat/MutableComponent;` |
| `minecraft/text/TextVisitFactoryMixin.java` | `visitFormatted(Ljava/lang/String;ILnet/minecraft/text/Style;Lnet/minecraft/text/CharacterVisitor;)Z` | `iterateFormatted(Ljava/lang/String;ILnet/minecraft/network/chat/Style;Lnet/minecraft/util/FormattedCharSink;)Z` |
| `client/ClientPlayerInteractionManagerMixin.java` | `method = {"handleInventoryMouseClick"}` | `method = {"handleContainerInput"}` |

Существенные детали этих правок:

- **`Entity.move` принимает `MoverType`, а не `MovementType`** — не переименование пакета, а другое имя класса.
- **`isControlledByClient()` удалён.** Замена выбрана не по сходству названия, а дизассемблированием: `Entity.move` трижды вызывает `isLocalInstanceAuthoritative()` (смещения 416, 526, 612), поэтому именно она — прямая замена. `@ModifyExpressionValue` без `ordinal` покрывает все три точки, как и раньше.
- **`StringDecomposer.visitFormatted` → `iterateFormatted`**, а `CharacterVisitor` → `FormattedCharSink`. В этом файле цель `@At` уже была переведена на новое имя раньше — устарела только строка `method`, то есть порт был выполнен наполовину.
- **`TeamMixin`:** `decorateName` → `getFormattedName`. По дизассемблированию `PlayerTeam.getFormattedName` порядок вставок тот же, что был у старого `decorateName` (prefix → name → suffix, три `MutableComponent.append`), поэтому `ordinal = 0` по-прежнему указывает на тот же аргумент и поведение не изменилось.
- **`ClientPlayerInteractionManagerMixin`:** обработчик уже имел правильную сигнатуру `(int, int, int, ContainerInput, Player, CallbackInfo)` — устарела только строка имени. Это важный случай: строка компилируется, тесты её не ловят, а при `required: true` она роняет игру.
- **`client/render/gui/screen/HandledScreenMixin.java`** — ещё два таких же дефекта, файл передан агенту с точными данными: `drawSlot(GuiGraphicsExtractor, Slot)` → `extractSlot(GuiGraphicsExtractor, Slot, int, int)` (дескриптор `extractSlot(Lnet/minecraft/client/gui/GuiGraphicsExtractor;Lnet/minecraft/world/inventory/Slot;II)V`, обработчик обязан принять два `int`), и `handleInventoryMouseClick` → `handleContainerInput`.

### Закрытые пункты «не проверено» из прошлых записей

- `TextureTarget(String, int, int, boolean, GpuFormat)` — 5 аргументов подтверждены; `CustomRenderTarget` наследует `RenderTarget(String, boolean, GpuFormat)`, `GpuFormat.RGBA8_UNORM` существует.
- `BlendFunction.ADDITIVE` не существует; аддитивность везде `new BlendFunction(SRC_ALPHA, ONE)`.
- `MobEffectInstance(Holder<MobEffect>, int, int, boolean, boolean)` существует — снят вопрос по `FastBreak`.
- `Registry.getValue(Identifier)` возвращает значение напрямую (в отличие от `get(Identifier)`, возвращающего `Optional<Holder.Reference<T>>`).
- `Items.STAINED_GLASS_PANE` — теперь `ColorCollection<Item>`; отдельные константы вида `LIME_STAINED_GLASS_PANE` убраны, доступ через `.pick(DyeColor.LIME)`.
- `ColorCollection<T>.pick(net.minecraft.world.item.DyeColor)` возвращает `T`.

### Массовые причины ошибок

- 94× `handleInventoryMouseClick(int,int,int,ContainerInput,LocalPlayer)` → `handleContainerInput(int,int,int,ContainerInput,Player)`: та же арность и порядок, имя изменено, последний параметр расширен с `LocalPlayer` до `Player`.
- 78× `selected has private access in Inventory` — закрыто **двумя строками access widener** (`accessible` + `mutable` для `Inventory.selected`), а не переписыванием 78 мест вызова. Это сохраняет исходную семантику и не трогает логику.
- 20× `InputConstants.isKeyDown(Window, int)` — принимает `Window`, не `long`.
- `Camera` — аксессоры в стиле record: `position()`, `xRot()`, `yRot()`, `entity()` вместо `getPosition()`/`getYRot()`/`getXRot()`.
- `Entity.getScoreboard()` → `player.level().getScoreboard()`; `BlockPos.getCenter()` → `Vec3.atCenterOf`; `getArmorSlots()` → `getItemBySlot(EquipmentSlot)`; `GameProfile.getName()` → `name()`; `ResourceKey.location()` → `identifier()`.
- `ServerboundContainerClickPacket` — значение карты стало `HashedStack`, порядок аргументов «карта, затем carried» изменён.
- `Connection.send(Packet, PacketSendListener)` → только `send(Packet)`, `send(Packet, ChannelFutureListener)`, `send(Packet, ChannelFutureListener, boolean)`.

### Правки, сделанные вручную

- `gradle.properties` — путь к JDK 25 (см. выше).
- `wyvern.accesswidener` — `Inventory.selected`.
- `DrawUtil.java` — отсутствующий импорт `VanillaPipelines`.
- `Keyboard.java` — `isKeyDown` на `Window`.
- четыре миксина из таблицы выше.

### Потери поведения, зафиксированные честно, а не спрятанные

- `AutoExplosion` — флаг `usingSecondaryAction` исчез из формата `ServerboundInteractPacket` в 26.2; сохранять нечего. Пакет заменён на `ServerboundAttackPacket(id)`, который шлёт ванильный `MultiPlayerGameMode.attack`.
- `AltManagerScreen` — `EditBox.setFilter` удалён полностью; ограничение набора символов сохранено через `setResponder` (символы отбрасываются, а не блокируются на нажатии). Это адаптация, а не 1:1.
- `AltManagerScreen` — `User.Type` удалён; тип сессии пометить больше нельзя.
- `EnchantCustom` / `AutoBuyUtil` / `NbtItemBuy` — разворачивание `Optional` выполнено через перегрузки `getStringOr`/`getIntOr`/`getCompoundOrEmpty`/`getListOrEmpty`, воспроизводящие **дореформенную** семантику (отсутствие ключа → `""`/`0`/пустой тег/пустой список), а не через `get()`/`orElseThrow()`. Здесь неверный фолбэк молча менял бы, какие зачарования покупаются.

### Компиляция закрыта

`./gradlew compileJava` → **0 ошибок**. `./gradlew build` → **BUILD SUCCESSFUL**, на выходе `build/libs/karitsa-0.2-mc26.2.jar` (14.7 МБ), `-thin.jar`, `-sources.jar`. Annotation-процессор миксинов не выдал ни одного предупреждения о неразрешимых целях.

Осталось пройти рантайм-проверку (см. ниже).

### Замены, подтверждённые javap и применённые в этой волне

Все ниже — не по догадке, а по сигнатурам из JAR 26.2:

| Удалено | Замена | Чем подтверждено |
|---|---|---|
| `Options.hideGui` | `mc.gui.hud.isHidden()` | поля `hideGui` нет нигде в jar; `Gui.hud` public final, `Hud.isHidden()`/`Hud.toggle()` |
| `GameProfile.getName()` | `name()` | `GameProfile` стал record |
| `PlayerSkin.texture()` | `skin.body().texturePath()` | `PlayerSkin` — record, `body()` → `ClientAsset$Texture`, у которого `texturePath()` → `Identifier`; сверено с байткодом `PlayerFaceExtractor` и `PlayerSkinWidget` |
| `PrimitiveTopology.LINE_STRIP` | `DEBUG_LINE_STRIP` | в enum есть только `DEBUG_LINE_STRIP`, `TRIANGLE_STRIP`, `LINES` и т.д. — без «обычного» `LINE_STRIP` |
| `Camera.getYRot()` | `yRot()` | аксессор в стиле record |
| `Inventory.armor` | `player.getItemBySlot(EquipmentSlot.FEET/LEGS/CHEST/HEAD)` | поля `armor` в `Inventory` нет; экипировка переехала на `EntityEquipment` (`Inventory(Player, EntityEquipment)`). Порядок списка сохранён |
| `InventoryScreen.renderEntityInInventory(...)` | `InventoryScreen.extractEntityInInventoryFollowsMouse(GuiGraphicsExtractor,int,int,int,int,int,float,float,float,LivingEntity)` | единственный оставшийся вариант |
| `GuiGraphicsExtractor.drawString(...)` | `text(Font,String,int,int,int[,boolean])` | javap |
| `GuiGraphicsExtractor.renderItem(ItemStack,int,int)` | `item(ItemStack,int,int[,int])` | javap |
| `Matrix3x2fStack.pushPose/popPose` | `pushMatrix()`/`popMatrix()`; `translate`/`scale` только 2D — третий аргумент убран | joml `Matrix3x2fStack` |
| `RenderSystem.enableBlend/defaultBlendFunc/depthMask/disableBlend` | ничего: смешивание и глубина теперь свойства `RenderPipeline` | в `RenderSystem` этих методов больше нет вообще. В `HeldItemRendererMixin` контур `ItemDym` рисуется через `ShaderHandsRenderer.getCustomShaderKey`, чей пайплайн контура собран с `ColorTargetState(BlendFunction.TRANSLUCENT)` и пустым depth-stencil — то есть ровно тем состоянием «blend без записи глубины», которое раньше выставлялось глобально |
| `DynamicTexture(NativeImage)` | `DynamicTexture(Supplier<String>, NativeImage)` | остальные три конструктора требуют размеров |
| `ItemTags.DOORS` | `WOODEN_DOORS` — но см. ниже | `ItemTags.DOORS` исчез; `BlockTags.DOORS` (все двери) остался |
| `BlockTags.SAPLINGS` | `ItemTags.SAPLINGS` | тег переехал из `BlockTags` в `ItemTags` |
| `Level.getSkyColor(Vec3,float)` / `Level.getTimeOfDay(float)` | `camera.attributeProbe().getValue(EnvironmentAttributes.SKY_COLOR, tickDelta)` и `...SUN_ANGLE` с переводом в радианы | дизассемблирован `SkyRenderer.extractRenderState`: он берёт `SKY_COLOR` как `int` без преобразований и умножает `SUN_ANGLE` на `0.017453292f` (π/180) — то есть значение в **градусах**, а `Math.toRadians` в нашей правке эквивалентен |
| `ClientLevel` — нет ни `getSkyColor`, ни `getTimeOfDay` | см. выше | grep по классу пуст |
| `MultiPlayerGameMode.handleInventoryMouseClick` | `handleContainerInput(int,int,int,ContainerInput,Player)` | javap |
| `InputConstants.isKeyDown(long,int)` | `isKeyDown(Window,int)` — убрать `.handle()` | javap |

**Отдельно про `ItemTags.DOORS`:** в 26.2 ванильный тег разошёлся на `WOODEN_DOORS` (предметы) и `BlockTags.DOORS` (все двери). В `HmiHeldItemRendererMixin` проверка `item.is(ItemTags.DOORS)` решала «это дверь», и замена на `WOODEN_DOORS` молча выбросила бы железные двери. Чтобы поведение не изменилось, взято `Block.byItem(item.getItem()).defaultBlockState().is(BlockTags.DOORS)` — тот же приём, что уже используется рядом для `GLASS_PANES`, `RAILS`, `CLIMBABLE`.

### Инфраструктура dev-запуска

Первый `./gradlew runClient` упал **до** запуска Minecraft:

```
Mod 'karitsaDLC' (wyvern) 1.0-SNAPSHOT requires any version of fabric, which is missing!
FabricLoader/Resolution: Immediate reason: [HARD_DEP_NO_CANDIDATE wyvern 1.0-SNAPSHOT {depends fabric @ [*]}]
```

Причина оказалась не в коде мода и не в `build.gradle`. **В `fabric.mod.json` было указано устаревшее имя мода Fabric API.** Корневой `fabric.mod.json` бандла `fabric-api-0.161.0+26.2.jar` объявляет `"id": "fabric-api"`; идентификатор `fabric` больше не существует, поэтому загрузчик не находил зависимость. Исправлено `"fabric": "*"` → `"fabric-api": "*"`.

Попутно выяснено, почему `modImplementation` в этом проекте не существует (`Could not find method modImplementation()`), — это **не** версия Loom и **не** ошибка конфигурации:

- MC 26.2 поставляется **необфусцированным**, о чём Loom прямо сообщает при загрузке: `FabricLoader/Mappings: Mappings not present!`
- Loom в таком окружении отказывается создавать `mod*`-конфигурации: `Cannot get remap configurations in a non-obfuscated environment`. Перемаппировать нечего, поэтому конфигураций нет вообще — ни `modImplementation`, ни `modApi`, ни `modRuntimeOnly`.
- Проверено эмпирически: список конфигураций содержит только `modCompileClasspath`, `modCompileClasspathMapped`, `productionRuntimeMods` и семейство `minecraft*`.
- Следствие: Fabric API подключается обычным `implementation`. Бандл несёт корневой `fabric.mod.json`, поэтому загрузчик подхватывает его прямо с dev-classpath.

Это же объясняет, почему падение выглядело как проблема зависимостей, а не как ошибка порта — до применения миксинов дело не дошло.

### Осталось

- Валидатор GLSL по всем программам не прогонялся.
- Клиент на 26.2 запускается впервые. Компиляция и загрузка миксинов — разные проверки; аудит дескрипторов выше снижает риск падения при загрузке, но не заменяет запуск. Результат запуска пока не получен.


