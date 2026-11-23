"""第5回 宿題（発展）: 用語を入口にする Graph のテスト。APIキーは不要。"""

from app.retrieval import matching_lines, search_term_pages


def test_term_search_returns_every_page_that_mentions_the_term():
    result = search_term_pages("第2回 構造化出力")
    term = next(t for t in result["terms"] if t["term"] == "構造化出力")
    assert term["page_count"] == 12
    found = {(p["lecture"], p["page"]) for p in term["pages"]}
    assert (2, 53) in found  # ベクトル検索の上位5件には入らなかったページ


def test_unknown_term_returns_no_terms():
    assert search_term_pages("存在しない用語xyz") == {"terms": []}


def test_matching_lines_keeps_only_sentences_with_the_term():
    lines = matching_lines("形を守らせるなら構造化出力が先。口調はFTで直す。", ["構造化出力"])
    assert lines == ["形を守らせるなら構造化出力が先。"]


def test_explaining_pages_get_full_text_and_passing_mentions_get_one_sentence():
    term = search_term_pages("構造化出力")["terms"][0]
    pages = {(p["lecture"], p["page"]): p for p in term["pages"]}
    # 章の名前に用語があるページ（第3回 Part 5）は全文
    assert "スキーマ" in pages[(3, 34)]["content"]
    # 主題が別のページ（第2回 p.53）は、用語が出てくる文だけ
    assert "構造化出力" in pages[(2, 53)]["content"]
    assert len(pages[(2, 53)]["content"]) < 100
