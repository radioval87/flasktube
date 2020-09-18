function change_to_form()
{
    var post = document.getElementById('start');
    post.innerHTML = 
    "<form id='add_post' action='' method='post'>\
    <textarea id='text_area' name='new_post' rows='2' onkeyup='textarea_resize(event, 33, 2);'></textarea>\
    <div id='text_area_div'></div>\
    <input input id='submit_button' type='submit' value='Post'>\
    </form>";
    return false;
}

function comment_form(ID)
{
    var comment = document.getElementById(ID);
    comment.innerHTML = 
    "<div class = 'new_comment'>\
    <textarea id='text_area' name='new_comment' rows='2' onkeyup='textarea_resize(event, 32, 2);'></textarea>\
    <div id='text_area_div'></div><br><br>\
    <input input id='submit_button' type='submit' value='Comment'>\
    </div>\
    </form>";
    return false;
}

function textarea_resize(event, line_height, min_line_count)
{
  var min_line_height = min_line_count * line_height;
  var obj = event.target;
  var div = document.getElementById(obj.id + '_div');
  div.innerHTML = obj.value;
  var obj_height = div.offsetHeight;
  if (event.keyCode == 13)
    obj_height += line_height;
  else if (obj_height < min_line_height)
    obj_height = min_line_height;
  obj.style.height = obj_height + 'px';
}

function autosubmit(ID)
{
    var input = document.querySelector(ID); 
    input.onchange = function() 
    {                
        this.form.submit();
    }
}

function submit(ID)
{
  onclick=document.getElementById(ID).submit();
  event.preventDefault();
  return false; 
}

function hide(ID)
{
    var something = document.getElementById(ID);
    something.innerHTML = "";
    return false;
}
