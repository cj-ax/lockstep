I've built the Billing page as two desktop frames (1440px wide) in your learned-library draft, on a new page called "Billing". Both frames score 100% faithful to the library and I checked both in screenshots, but the dialog only looks right because of a separate fix I ran after the build, explained below.

**Link:** https://www.figma.com/design/iuJn7Ziu80PUNh9gVTM3LK/?node-id=8-259
The finished frames are on the bottom row: `Billing / Overview / v3` and `Billing / Dialog / v3`. The rows above are earlier passes, kept for comparison.

**How faithfully it uses your library**

| Pass | Library parts | Values tied to tokens | Detached | Hard-coded colours | Auto layout | Score | What I saw in the screenshots |
|---|---|---|---|---|---|---|---|
| v1 | 100% | 100% | 0% | 0% | 100% | 100 | Dialog buttons still said "Button"; plan buttons didn't reach the card's right edge; header showed marketing links and "Sign in / Register" |
| v2 | 100% | 100% | 0% | 0% | 100% | 100 | Header fixed; the other two problems remained |
| v3 | 100% | 100% | 0% | 0% | 100% | 100 | Overview clean. Dialog clean after the extra fix |

Every visible part is a library component with its options set explicitly. All spacing and the page background use your tokens. Nothing is detached or drawn by hand. I took the v3 score before the dialog fix and didn't rescore afterwards. The fix only renamed the two buttons and switched one to your Button Danger component, so the score shouldn't change.

The score can't be trusted on its own: it gave 100 while the dialog buttons still read "Button". It doesn't check placeholder text in components placed inside another component's content area.

**Decisions I made**
- **Header:** your Header component comes with marketing links and a signed-out state. I renamed the links to Dashboard, Projects, Team and Billing, highlighted Billing, hid the extra links, and switched it to its "Logged In" state. Those page names are my invention.
- **Current plan card:** "Pro plan" on the left and "$24 per month" on the right, with a line underneath: "Billed monthly. Your next payment is on 1 November 2026." The plan name, price and date are made up.
- **Plan actions:** Change plan is the main button. Cancel subscription uses your red Button Danger in its quieter Subtle style, and it sits to the right of Change plan. I wanted it on the left, but Figma breaks the layout when the first button in your learned Button Group is replaced, so it went in the second position.
- **Save button:** I added Cancel and Save changes to the Payment details card, using your learned Button Group with its own labels. You didn't ask for this, but editable fields need a way to save.
- **Sample card details:** Jordan Lee, a masked card number ending 4242, 08 / 28, and billing@example.com.
- **Dialog:** your learned Dialog covers the whole screen and has a plain white background, so the second frame doesn't show the Billing page behind it. The buttons are Keep subscription and a red Cancel subscription. The message reads: "Your Pro plan stays active until 1 November 2026. After that, your team moves to the Free plan and loses access to Pro features." I wrote that wording.

**What isn't finished**
- **The dialog needs a second script.** Inside the main build, the button labels and the swap to the red button silently don't take effect. The same edits work when run on their own afterwards, so rebuilding means running `build-billing.js` and then `fix-billing-dialog.js` (both under `lockstep/` in the project folder).
- **No component for parts of the brief:** everything is assembled from library parts, so nothing is labelled "Not in library". But the library has no component for showing a plan and its price, and Card (Slot) has no subtitle.

**Gaps to pass to the design-system team**
- Switch Field was learned with only its "on" state, so this page can't show the receipts setting turned off.
- Header defaults to marketing navigation; an app version would help.
- Card (Slot) has no subtitle option, and there's no component for a plan name with a price.
- Dialog has no version that shows the page dimmed behind it.
- Replacing the first button of the learned Button Group breaks its layout in Figma.

The page is built from your library components plus your Inter text styles (Inter is under the SIL Open Font License). I added no other fonts or libraries.