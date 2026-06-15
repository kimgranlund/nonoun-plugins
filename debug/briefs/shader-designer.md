# Creative Animated Shader Designer

Build a browser tool for designing animated fragment shaders with a live preview and shareable presets. WebGL
for the canvas; no build step (or a tiny Vite app).

## What a good version does

- A live **WebGL fragment-shader** canvas animating in real time (a `u_time` uniform, resolution, mouse).
- An editor pane: edit GLSL with a debounced recompile; **compile errors are shown inline** (line + message),
  never a blank canvas.
- **Uniform controls**: auto-detect `uniform float`/`vec` declarations and generate sliders/color pickers that
  drive them live.
- **Presets**: save/load named presets (the shader source + uniform values) to localStorage; a gallery of a few
  built-in starters (plasma, gradient noise, raymarched sphere).

## Non-goals

- No multi-pass / compute, no texture uploads in the first cut.
- No backend; presets are local only.

## Acceptance signal

Editing the GLSL recompiles live; a syntax error surfaces a readable message instead of breaking; a detected
uniform gets a working control; a preset round-trips through a reload. **Build the uniform-parser + the
preset (de)serializer as pure ES modules** (`parseUniforms(src) → [{name,type,...}]`, `serializePreset` /
`deserializePreset`) a `verify.mjs` checks headlessly — the GL rendering stays in the shell.
