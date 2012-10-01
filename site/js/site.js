function CalendarCtrl($scope) {
  var now = moment().startOf('day');

  $scope.days = [];
  for (var i = 0; i < 7; i++) {
    $scope.days.push(now.clone().toDate());
    now.add('days', 1);
  }

  $scope.hours = ["12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM",
    "6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
    "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM",
    "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"];

  $scope.addTodo = function() {
    $scope.todos.push({text:$scope.todoText, done:false});
    $scope.todoText = '';
  };

  $scope.remaining = function() {
    var count = 0;
    angular.forEach($scope.todos, function(todo) {
      count += todo.done ? 0 : 1;
    });
    return count;
  };

  $scope.archive = function() {
    var oldTodos = $scope.todos;
    $scope.todos = [];
    angular.forEach(oldTodos, function(todo) {
      if (!todo.done) $scope.todos.push(todo);
    });
  };
}
$(function() {

  var isMouseDown = false;
  var togglingOn = true;

  $("#meme td")
  .mousedown(function () {
    if (!$(this).hasClass("cellWhite")) {
      isMouseDown = true;
      togglingOn = !$(this).hasClass("highlighted");
      $(this).toggleClass("highlighted", togglingOn);
    }
    return false; // prevent text selection
  })
  .mouseover(function () {
    if (!$(this).hasClass("cellWhite")) {
      if (isMouseDown) {
        $(this).toggleClass("highlighted", togglingOn);
      }
      $('.profile').addClass('faded');
      $.each($(this).data('userids'), function (i, userid) {
        $('.profile-'+userid).removeClass('faded');
      });
    }
    if ($(this).data('count')) {
      $(this).data('time', $(this).text());
      $(this).text($(this).data('count'));
    }
  })
  .mouseout(function () {
    if ($(this).data('time')) {
      $(this).text($(this).data('time'));
    }
    $('.profile').removeClass('faded');
  });

  $(document).mouseup(function () {
    isMouseDown = false;
  });

  $("#fb-event-list a").click(function() {
    var id = $(this).data('id');
    $("#fb-event-id").val(id);
    $("#go").removeAttr("disabled").val("Go »");

    $("#fb-event-list li").removeClass("active");
    $(this).parent("li").addClass("active");
    return false;
  })

  $("#create-form").submit(function(e) {
    // e.preventDefault();

    var $table = $("#meme"),
        $rows = $table.find("tbody tr");

    var headers = [],
        rows = [];
    $rows.each(function(row,v) {
      $(this).find("td").each(function(cell,v) {
        if (typeof rows[cell] === 'undefined') rows[cell] = [];
        rows[cell][row] = $(this).hasClass("highlighted");
      });
    });

    var days = $.map(rows, function (truefalse, cell) {
      return [$.map(truefalse, function (v, row) {
        if (v) {
          return row;
        }
      })];
    });

    $("#fb-times").val(JSON.stringify(days));
  });
});
