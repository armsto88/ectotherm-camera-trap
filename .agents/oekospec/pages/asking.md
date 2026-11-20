# Asking in rounds

How discuss, propose and implement put their questions to the user. Read this before your first
round.

## Rounds
- Put your questions in rounds. A round holds every question that can be answered now: each
  question that depends on no answer still open. Questions of different topics may share a
  round.
- A question that follows from an answer comes in the next round, and only if that answer
  raises it. Don't plan rounds ahead as a list; each builds on the answers before it.

## Page or chat
- A round with two or more open questions, or with an option that changes something visible,
  goes on a decision page.
- A round with a single open question where nothing visible changes is asked in the chat: the
  question, your recommended answer and one short reason. Open no page for it.

## What an open question holds
Each open question on a page must be understandable without the chat:
- `title`: the question, in plain words.
- `context`: one or two sentences: what it is about and why it comes up now.
- `more`: where there is more to say, the background, already filled in. The page shows it
  folded under "More context". Write it so the user rarely needs the chat.
- `options`: two or more, each with a short `label`, a `text` and its weakness in `weak`. Mark
  exactly one with `"rec": true` and give its reason in `why`. The page marks it but does not
  select it.
- `free`: sketches, pictures, drafts or anything else the question needs (see below).

The page adds a note field and "Rather discuss in the chat" to every question, and a free field
at its end. Write in plain words, avoid abbreviations and technical terms where plain words
work, and name no internals the user doesn't need to decide.

## Open, confirm and collapsed
- **Open** (`open`): a question where the user may plausibly decide differently from your
  recommendation, or that likely matters to them.
- **Collapsed** (`collapsed`): every other question. Its `title` states the decision, such as
  "Dates are shown in the user's time zone", with `why` and, where there is one, the
  alternative in `alt`. It is carried out as its title says unless the user changes it.
- **Confirm** (`confirm`): points the user settled in the chat since the last page, worded as
  they will be logged; and a solution the user proposed in a note, with its weakness in `weak`
  or the alternative you weighed it against in `rejected`. Such a solution goes into the
  decision log only after this round confirms it.

## Sketches and pictures
- When an option changes something visible, such as a text or its place in a user interface,
  show a simple sketch for each option with the real text in the real place. Draw it from the
  building blocks below; don't start the app.
- When a question is about how parts connect or how a flow runs, show a picture of it. Where
  the question changes the connection or the flow, show it before and after, side by side.
- A question about wording or a plain yes or no gets no picture.

Building blocks, as HTML in `free`:

| Block | What it draws |
|---|---|
| `<div class="pair"><figure><figcaption>A</figcaption>…</figure><figure>…</figure></div>` | two things side by side, such as two options or before and after |
| `<div class="app"><div class="app-h">Title <span class="btn">Save</span></div><div class="app-b">…</div></div>` | a window or panel of the app, with its title bar and body |
| `<div class="field"><span class="label">From</span>2026-01-01</div>` | an input field with its label |
| `<div class="hint">…</div>`, `<span class="tip">…</span>` | a help text under a field, a tooltip |
| `<span class="btn">…</span>`, `<div class="infobox">…</div>` | a button, an info box |
| `<span class="mark">…</span>` | new or changed text, highlighted |
| `<div class="flow"><span class="box">A</span><span class="arrow">label</span><span class="box">B</span></div>` | boxes joined by arrows, left to right; `flow down` runs top to bottom |
| `<span class="box new">…</span>`, `<span class="box gone">…</span>` | a part that is added, a part that goes |
| `<div class="draft">…</div>`, `<div class="mono">…</div>` | a draft text, text as it stands in a file |

## The free area
When a question needs something the template lacks, such as a table, add it in that question's
`free`. Scope any style you add to a class of your own, such as
`<style>.my-table td { padding: 4px }</style>`, and keep the frame, buttons and sending as the
template has them. When you notice the same thing missing again and again, tell the user it
could go into the template, as feedback to the oekospec repo.

## Language
Write the page in the language of the conversation and set `language` to its code, such as `en`
or `de`. The template brings its labels in English and German. For another language, add
`labels` to the round: every key of `en` in `.agents/oekospec/pages/labels.json`, translated.
The decision log and every other file stay in English.

## The round file
Write the round as a JSON file outside the repository, such as in the system's temp folder.
`open`, `confirm` and `collapsed` may each be left out when empty. `intro`, `more` and `free`
hold HTML; every other field is plain text. Ids start with a letter and are unique in the
round; `chat` is no option id.

```json
{
  "language": "en",
  "step": "discuss",
  "change": "add-export-date-range",
  "round": 2,
  "title": "Where the date range goes",
  "intro": "<p>Round 1 is in the log, entries 1 to 3.</p>",
  "open": [
    {
      "id": "q1",
      "title": "Where does the help text of the date range appear?",
      "context": "The new filter gets a short help text: \"Filters by the date of the measurement.\"",
      "more": "<p>Most users of the export work on tablets, where nothing shows on hover.</p>",
      "free": "<div class=\"pair\"><figure><figcaption>A · Under the field</figcaption><div class=\"app\"><div class=\"app-h\">Export</div><div class=\"app-b\"><div class=\"field\"><span class=\"label\">From</span>2026-01-01</div><div class=\"hint\"><span class=\"mark\">Filters by the date of the measurement.</span></div></div></div></figure><figure><figcaption>B · In a tooltip</figcaption><div class=\"app\"><div class=\"app-h\">Export</div><div class=\"app-b\"><div class=\"field\"><span class=\"label\">From ⓘ</span>2026-01-01</div><span class=\"tip\"><span class=\"mark\">Filters by the date of the measurement.</span></span></div></div></figure></div>",
      "options": [
        {
          "id": "a",
          "label": "Under the field",
          "text": "Always visible below the date fields.",
          "rec": true,
          "why": "Users see it without searching, also on tablets.",
          "weak": "Takes one line of space."
        },
        {
          "id": "b",
          "label": "In a tooltip",
          "text": "Shows when the pointer rests on the info sign.",
          "weak": "Easy to miss, and does not work on tablets."
        }
      ]
    },
    {
      "id": "q2",
      "title": "Does the export try again before it reports an error?",
      "context": "Large exports sometimes fail once when the server is busy.",
      "free": "<div class=\"pair\"><figure><figcaption>Today</figcaption><div class=\"flow\"><span class=\"box\">Export</span><span class=\"arrow\">fails</span><span class=\"box\">Error</span></div></figure><figure><figcaption>With option A</figcaption><div class=\"flow\"><span class=\"box\">Export</span><span class=\"arrow\">fails</span><span class=\"box new\">Try once more</span><span class=\"arrow\">fails</span><span class=\"box\">Error</span></div></figure></div>",
      "options": [
        {
          "id": "a",
          "label": "Yes, once",
          "text": "One more try, then the error.",
          "rec": true,
          "why": "Most failures pass on their own.",
          "weak": "A real error shows a little later."
        },
        {
          "id": "b",
          "label": "No",
          "text": "The error shows at once, as today.",
          "weak": "Users start busy exports again by hand."
        }
      ]
    }
  ],
  "confirm": [
    {
      "id": "s1",
      "title": "The filter uses the date of the measurement, not the date it was entered.",
      "body": "Your proposal from round 1.",
      "weak": "Old records without a measurement date drop out of every range.",
      "rejected": "The entry date (late entries would land in the wrong range)."
    }
  ],
  "collapsed": [
    {
      "id": "k1",
      "title": "Dates are shown in the user's time zone.",
      "why": "As everywhere else in the app.",
      "alt": "Always in UTC"
    }
  ]
}
```

## Showing the page
Run `python3 .agents/oekospec page <round-file>`. It checks the round; if it lists problems,
fix the file and run it again. Otherwise it opens the page in the user's browser, or reuses the
tab of the last page, and waits up to four hours until the user sends. Then it prints the
answers as JSON and ends. Run it in the background where your tool allows, and wait for it to
end rather than asking the user in the chat meanwhile. If no browser opens, give the user the
address it printed. If the user pastes the answers as text instead, take them from there.

discuss ends on the review page: `python3 .agents/oekospec page --review <change>`, with
`--language de` for a conversation in German.

## Taking the answers
- `open`: `choice` is the option id the user picked, `chat` for "Rather discuss in the chat",
  or `null` for no answer; `note` is the user's note.
- `confirm` and `collapsed`: `keep` is true when the point stays as its title says. When it is
  false, the note is the user's answer instead of the title; a collapsed point changed without
  a note takes its `alt`.
- `review`: `edited` is true when the user changed the text; `markdown` then holds the new text
  as the user wrote it.
- `free`: the page's free field.

Take every answer not marked for the chat at once, and log the real choices among them. Then
take up the questions marked for the chat, one after the other. A solution the user proposes in
a note goes into the next round, with its weakness or an alternative, before it is logged.
