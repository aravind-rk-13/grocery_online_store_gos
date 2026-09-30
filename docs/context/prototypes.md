# App status and prototype images

## The app is in build (not live)
- The 7rmart admin console is being built. It is not a live product, and the console URL is **not usable yet**
  (`config/workflow.json` app.console_usable = false).
- While console_usable is false: never open, probe or log in to the console (no Playwright MCP, no probe scripts, no pytest
  runs against it). The sources are the CR page, the CR brief, the stories and the prototype images.
- The PM sets console_usable to true when a build is released for testing. Only then do agents check the real screens,
  record locators and run tests.
- The BRD (docs/7rmart_supermarket_brd.md) is a requirements reference. It does not describe what is built today.

## Prototype images are design, not the real workflow
- The PM supplies design prototypes as images. They show the intended layout, labels and flow for a CR.
- They are not proof that anything exists or works. Never conclude "already built" or "already works" from an image.
- Where: `docs/prototype_images/` (gitignored: images may contain realistic data).
  Name: `CR_<NNN>_image_<n>.png` (e.g. CR_002_image_1.png). The number orders the images in the flow.

## How every agent uses them
1. For a CR (e.g. CR-002), list `docs/prototype_images/CR_002_image_*.png` and read each one.
2. Use them to answer layout, label and flow questions: headings, columns, button names, popups, messages, counts,
   pagination. Cite the file in the source (e.g. "prototype CR_002_image_2").
3. The call notes and PM answers decide scope. When an image conflicts with them, raise an open question. Never pick
   one yourself.
4. Features that appear only in an image and not in the CR are out of scope (future work). List them, but don't
   write requirements or tests for them.
5. If there are no images for the CR, or they don't answer a point, ask it as an open question. Never guess.
6. Never copy names, phone numbers, emails or ids shown in an image into Jira, Confluence or files. Describe the
   structure only, and use placeholder tokens.

## Renamed files (2026-09-30)
Older Jira Tests (GOS-21..GOS-42) cite the old names.
| Old name | New name |
|---|---|
| side_navigation_bar.png | CR_001_image_1.png |
| admin_users_list.png | CR_001_image_2.png |
| pagination_1.png | CR_001_image_3.png |
| pagination_2.png | CR_001_image_4.png |
| verify_users.png | CR_002_image_1.png |
| delete_popup.png | CR_002_image_2.png |
| successful_deleted_message.png | CR_002_image_3.png |
