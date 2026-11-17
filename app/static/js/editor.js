(function () {
  var ta = document.getElementById('body');
  var host = document.getElementById('editor');
  var form = document.getElementById('postForm');
  if (!ta || !host || typeof Quill === 'undefined') return; // fallback: plain textarea
  ta.style.display = 'none';
  var q = new Quill(host, {
    theme: 'snow',
    placeholder: 'Write your story…',
    modules: { toolbar: [[{ header: [2, 3, false] }], ['bold', 'italic', 'underline'],
      [{ list: 'ordered' }, { list: 'bullet' }], ['blockquote', 'code-block', 'link'], ['clean']] }
  });
  if (ta.value.trim()) q.clipboard.dangerouslyPasteHTML(ta.value);
  form.addEventListener('submit', function () {
    ta.value = q.getText().trim() ? q.root.innerHTML : '';
  });
})();
