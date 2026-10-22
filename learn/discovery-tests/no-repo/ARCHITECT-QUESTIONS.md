# Questions about Acme's front-end stack

We're documenting Acme's design system so the Figma library and the code can be matched up. There's no repository to read, so these questions go to whoever knows how the product is built. Short answers are fine, and "I don't know" is a useful answer too.

## What the Figma files suggest

Please confirm or correct each one.

- The library's colours and spacing look like a custom scale (no MUI or Vuetify defaults found).
  - Right? 
- Component names (Card (Slot), Button Group, Switch Field) don't match any common UI library's names.
  - Right? 

## What the product is built with

1. Which framework do the web front ends use: React, Vue, Angular, Svelte, something else, or several?
   - Answer:
2. Do they use a component library such as MUI, Vuetify, Chakra, Ant Design, Bootstrap or shadcn/ui? Which version?
   - Answer:
3. How are styles written: CSS or Sass files, Tailwind, CSS-in-JS (styled-components, Emotion), or something else?
   - Answer:
4. Are there native mobile apps too? If so, do they share anything with the web (tokens, naming)?
   - Answer:

## Shared components

5. Is there a shared component library in code? Where does it live (repository, package name), and who owns it?
   - Answer:
6. Roughly how many components does it have, and do product teams install it or copy from it?
   - Answer:
7. Is there a Storybook or another place where the components are documented? Please share the link.
   - Answer:

## Design tokens

8. Where do colours, spacing, type sizes and radii come from in code: a tokens file, a theme object, Sass variables, or hard-coded values?
   - Answer:
9. Are tokens generated from somewhere (Tokens Studio, Style Dictionary, a Figma export), or written by hand?
   - Answer:
10. Are there themes or brands (light and dark, white-label clients)? How does the code switch between them?
   - Answer:

## Access

11. Can the design team get read access to the repository? If not, could you share the tokens file and a list of components with their props?
   - Answer:
12. Who should we ask when something in Figma and code disagree?
   - Answer:

Answered by: (name, role, date)
