SELECT * FROM warning_tpls_transcludes
JOIN pages ON warning_tpls_transcludes.page_id = pages.id
JOIN timecheck ON timecheck.page_id = pages.id
LEFT OUTER JOIN refs USING (page_id)
WHERE refs.page_id IS NULL

SELECT * FROM pages
LEFT OUTER JOIN warning_tpls_transcludes ON pages.id = warning_tpls_transcludes.page_id
LEFT OUTER JOIN refs ON pages.id = refs.page_id
WHERE warning_tpls_transcludes.page_id IS NULL
AND refs.page_id  IS NOT NULL
GROUP BY pages.id

с новыми правками или без проверки
SELECT * FROM pages JOIN timecheck ON pages.page_id = timecheck.page_id
WHERE pages.timelastedit > timecheck.timecheck OR timecheck.timecheck IS NULL

pages без warning
SELECT * FROM pages LEFT OUTER JOIN warnings ON pages.page_id = warnings.page_id WHERE warnings.page_id IS NULL

warnings без refs, к снятию warnings
SELECT * FROM warnings LEFT OUTER JOIN refs ON warnings.page_id = refs.page_id WHERE  refs.page_id IS NULL

titles for add warnings
SELECT pages.title FROM pages LEFT OUTER JOIN warnings ON warnings.page_id = pages.page_id
JOIN refs ON pages.page_id = refs.page_id
WHERE  warnings.page_id IS NULL AND refs.page_id  IS NOT NULL
-- ORDER BY pages.page_id, refs.citeref
GROUP BY pages.title

pages with errrefs
SELECT * FROM refs  GROUP BY refs.page_id
pages with errrefs and pagnames


SELECT * FROM pages LEFT OUTER JOIN  refs ON pages.page_id = refs.page_id
WHERE refs.page_id  IS NOT NULL
GROUP BY refs.page_id

LEFT OUTER JOIN warnings ON warnings.page_id = refs.page_id
JOIN pages ON warnings.page_id = refs.page_id
WHERE  warnings.page_id IS NULL
ORDER BY warnings.page_id, refs.page_id
-- JOIN timecheck USING (page_id)
-- ORDER BY warnings.page_id, refs.page_id
-- GROUP BY warnings.page_id


DELETE FROM timecheck WHERE page_id IN (
SELECT page_id, title
FROM warning_tpls_transcludes
LEFT OUTER JOIN refs USING (page_id)
JOIN pages ON pages.id = refs.page_id
WHERE refs.page_id IS NULL
GROUP BY refs.page_id
)


SELECT * FROM pages JOIN refs USING (page_id) JOIN timecheck USING (page_id) WHERE title LIKE 'Росянка'

SELECT refs.page_id FROM refs LEFT OUTER JOIN pages WHERE  pages.page_id IS NULL

удаление timecheck у страниц с warnings
DELETE FROM timecheck WHERE timecheck.page_id IN (
SELECT page_id FROM warnings
)

удаление timecheck у страниц с refs
DELETE FROM timecheck WHERE timecheck.page_id IN (SELECT page_id FROM refs GROUP BY page_id  )


SELECT * FROM pages JOIN refs USING (page_id) JOIN timecheck USING (page_id)
WHERE title LIKE 'Росянка'


move timecheck.timecheck → pages.timecheck
UPDATE pages SET timecheck = (SELECT timecheck.timecheck FROM timecheck WHERE pages.page_id = timecheck.page_id)
