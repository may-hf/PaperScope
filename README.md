# PaperScope v0.2 — daily automatic metadata candidates

## What works

- Mobile PWA, offline fallback, search, favorites, read status, JSON import/export.
- Loads `papers.json` on app launch and when pressing **更新を確認**; deduplicates by DOI/OpenAlex ID and keeps local reading state.
- GitHub Actions daily workflow fetches metadata candidates from OpenAlex, up to **5 Chemistry and 2 Geometry** per run, and commits `papers.json`.
- **Important:** Automatic items are *unreviewed candidates*, **not** the same as the existing ChatGPT daily digest. No AI Japanese summaries, publisher verification of corresponding authors, or automatic ChatGPT task synchronization. When source/API fails, the script does not invent entries.

## Publish and enable updates (GitHub Pages)

1. Create a GitHub repository, and upload **all contents of this folder including `.github/workflows/daily.yml`** to the repository root. GitHub web uploads of hidden directories can be awkward; Git command line or GitHub Desktop is more reliable.
2. In **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`. Wait for the HTTPS URL.
3. In **Actions**, run **Daily paper metadata update → Run workflow** once. It creates/populates `papers.json`. GitHub Actions may require enabling in repository settings. The daily cron `0 22 * * *` is 07:00 JST, but GitHub does not guarantee exact execution time.
4. Open the Pages URL in Android Chrome → **アプリをインストール** / **ホーム画面に追加**.
5. Reopen the app after 7am or press **更新を確認** to retrieve the latest feed. Data already imported stays on your device.

**Netlify Drop** can host the app, but does **not** automatically run the included GitHub Actions workflow. For scheduled updates use GitHub (or an equivalent scheduler) and ensure the updated `papers.json` is deployed.

## Accuracy and privacy

- OpenAlex search is heuristic, not a comprehensive check of all journals or exact publication dates; metadata may be incomplete. It cannot replace publisher-based author verification. Items clearly indicate that summaries and corresponding authors are unverified.
- The auto feed is public if the repository/site is public. Read status and favorites are stored only in localStorage on each device.
- The existing six papers are **demo entries**; check against original publications before citing.
- For full Japanese summaries and author verification, a later version needs a separate LLM+publisher verification pipeline and a secure server-side API key (never embed keys in HTML).
