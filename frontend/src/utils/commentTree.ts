import type { CommentTreeNode, CourseComment } from '@/types'

function buildNode(
  comment: CourseComment,
  byParent: Map<number, CourseComment[]>,
  depth: number,
  rootId: number,
  sortFn: (a: CourseComment, b: CourseComment) => number,
): CommentTreeNode {
  const children = (byParent.get(comment.id) ?? [])
    .slice()
    .sort(sortFn)
    .map(c => buildNode(c, byParent, depth + 1, rootId, sortFn))
  return { comment, depth, rootId, children }
}

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
  const rootCmp = sortMode === 'date' ? sortByDate : sortByPopular
  return roots
    .slice()
    .sort(rootCmp)
    .map(root => buildNode(root, byParent, 0, root.id, sortByDate))
}

export function flattenDescendants(node: CommentTreeNode): CommentTreeNode[] {
  const result: CommentTreeNode[] = []
  for (const child of node.children) {
    result.push(child)
    result.push(...flattenDescendants(child))
  }
  return result
}
