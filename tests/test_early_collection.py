import unittest
from early.collect import Text, safe_url, validate_reviewed, article_url

class CollectionTests(unittest.TestCase):
    def test_html_preserves_measure_lines_and_ignores_script(self):
        p=Text();p.feed("<p>Stadt Roth: 1 Millionen Euro für</p><script>fake</script><li>Neubau</li>")
        self.assertNotIn("fake",p.text)
        self.assertIn("\n",p.text)

    def test_url_boundary(self):
        for url in ("http://example.org/x","https://example.org.evil/x","https://user:pw@example.org/x"):
            self.assertFalse(safe_url(url,"example.org"))
        self.assertTrue(safe_url("https://example.org/x","example.org"))

    def test_only_reviewed_date_and_project(self):
        doc=dict(source_url="https://example.org/x",published="2026-07-21",date_anchor="21.07.2026",
            records=[dict(required_anchor="Klinikum Traunstein",event=dict(source_url="https://example.org/x",published="2026-07-21"))])
        self.assertEqual(len(validate_reviewed(doc,"21.07.2026 Klinikum Traunstein")),1)
        for text in ("Klinikum Traunstein", "21.07.2026 unrelated project"):
            with self.assertRaises(ValueError): validate_reviewed(doc,text)

    def test_discovery_keeps_article_title_and_publication_metadata(self):
        page=Text()
        page.feed('<meta property="article:published_time" content="2026-08-18T10:00:00"><a href="/x">Neue <b>Schule</b></a>')
        self.assertIn("Schule",page.link_titles["/x"])
        self.assertEqual(page.publication_dates,["2026-08-18T10:00:00"])

    def test_only_main_article_publication_date_is_used(self):
        source="https://example.org/main"
        page=Text(source)
        page.feed('<script type="application/ld+json">{"@graph":[{"@type":"NewsArticle","url":"https://example.org/other","datePublished":"2026-10-06"},{"@type":"NewsArticle","url":"https://example.org/main","datePublished":"2026-08-18"}]}</script>')
        self.assertEqual(page.publication_dates,["2026-08-18"])
        self.assertNotIn("2026-10-06",page.text)

    def test_curated_summary_articles_do_not_break_source_verification(self):
        doc=dict(source_url="https://example.org/x",published="2026-07-21",date_anchor="21.07.2026",
            records=[dict(required_anchor="Generalsanierung, Umbau und Erweiterung der Schule",
                event=dict(source_url="https://example.org/x",published="2026-07-21"))])
        self.assertEqual(len(validate_reviewed(doc,"21.07.2026 Generalsanierung, den Umbau und die Erweiterung der Schule")),1)
        with self.assertRaises(ValueError):
            validate_reviewed(doc,"21.07.2026 Generalsanierung, Umbau und Erweiterung des Kindergartens")
    def test_dated_publisher_permalink_is_explicit_provenance(self):
        url="https://example.org/2026/08/18/main/"
        doc=dict(source_url=url,published="2026-08-18",date_anchor="2026-08-18",date_basis="publisher_permalink",
            records=[dict(required_anchor="Gymnasium Hochrad",event=dict(source_url=url,published="2026-08-18"))])
        self.assertEqual(len(validate_reviewed(doc,"Gymnasium Hochrad")),1)
        with self.assertRaises(ValueError):
            validate_reviewed(dict(doc,published="2026-08-19"),"Gymnasium Hochrad")

    def test_discovery_accepts_canonical_paths_with_or_without_trailing_slash(self):
        for url in ("https://example.org/internet/stmf/aktuelles/pressemitteilungen/26385",
                    "https://example.org/internet/stmf/aktuelles/pressemitteilungen/26385/",
                    "https://example.org/press/pressemitteilungen/neubau-schule-1210668"):
            self.assertTrue(article_url(url,"example.org"))
        self.assertFalse(article_url("https://example.org/kommunaler_finanzausgleich/hochbauten/","example.org"))
        self.assertFalse(article_url("https://evil.org/pressemitteilungen/26385","example.org"))
