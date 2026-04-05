import type { CommentTreeNode, CourseComment } from '@/types'

export function buildCommentTree(
  flat: CourseComment[],
  sortByDate: (a: CourseComment, b: CourseComment) => number,
  sortByPopular: (a: CourseComment, b: CourseComment) => number,
  sortMode: 'date' | 'popular',
): CommentTreeNode[] {
  const roots = flat.filter(c => c.parentId == null)
  const byParent = new Map<number, CourseComment[]>()
  for (const c of flat) {
    if (c.parentId != null) {
      const list = byParent.get(c.parentId) ?? []
      list.push(c)
      byParent.set(c.parentId, list)
    }
  }
  const cmp = sortMode === 'date' ? sortByDate : sortByPopular
  roots.sort(cmp)
  for (const list of byParent.values())
    list.sort(sortByDate)

  return roots.map(root => ({
    root,
    replies: (byParent.get(root.id) ?? []).sort(sortByDate),
  }))
}
