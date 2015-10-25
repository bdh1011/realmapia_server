
	$(document).ready(function(){
		
		$(".search_icon").click(function(){
			window.location.href = '/manage/main?search=' + $(this).parent().find('#search').val()
		})
		$("#assign_room").click(function(){
			to_assign_room_list = []
			$("#assign_room_box").fadeIn()
				.css({display:'block'})
				.animate({opacity:1}, 500, function() {
				    //callback
			});

			$(".room_wrapper").css({marginBottom:284})
			$(".assigned_room_overlay").fadeIn().css({'display':'block'});
			$(".assigned_room_overlay").click(function(){
				
				$(this).children('.assign_check').toggle();
				var room_num = $(this).parent().attr('data-room-num');
				console.log(room_num);
				
				var index = to_assign_room_list.indexOf(room_num);
				if (index > -1) {
				    to_assign_room_list.splice(index, 1);
				}
				else{
					to_assign_room_list.push(room_num);
				}
				console.log(to_assign_room_list);
				$('#employee_info_rooms textarea').text(to_assign_room_list);
			});

			var get_team_list =	$.ajax({ 
				type: "GET", 
				url: "/manage/teams",
				contentType: "application/json; charset=utf-8", 
				dataType: "json"
			});
			var update_team_list = function(data){
				var team_list_html = ''
				team_list = data['team_list']
				for(i in team_list){
					team_list_html += '<li class="assign_box_team_li">'+team_list[i]+'</li>\n'
				}
				$("#team_list ul").html(team_list_html);
			}

			function team_click_listner(){
				$(".assign_box_team_li").click(function(){

					$(".assign_box_team_li").each(function(){
						$(this).css({'backgroundColor':'#ffffff'})
					})
					$(this).css({'backgroundColor':'#d3eff9'})
					$.ajax({ 
						type: "GET", 
						url: "/manage/employee?team="+$(this).text(),
						contentType: "application/json; charset=utf-8", 
						dataType: "json", 
					}).then(update_employee_list).then(employee_click_listener);
				})
			};
			employee_list = []

			var update_employee_list = function(data){
				var employee_list_html = ''
				employee_list = data['result']

				for(i in employee_list){
					employee_list_html += '<li data-employee-id="'+employee_list[i]['id']+'">\
					<div class="employee_name">'+employee_list[i]['name']+'</div>\
					<div class="employee_assign">'+employee_list[i]['is_assigned']+'</div>\
					<div class="employee_room">'+employee_list[i]['assigned_room_list']+'</div>\
					</li>\n'
				}
				$("#assign_room_box #employee_list ul").empty();
				$("#assign_room_box #employee_list ul").append(employee_list_html);
			};


			function employee_click_listener(){
				$("#employee_list ul li").click(function(){
					var employee_id = $(this).attr("data-employee-id");
					$("#employee_list ul li").each(function(){
						$(this).css({'backgroundColor':'#ffffff'})	
					})
					$(this).css({'backgroundColor':'#d3eff9'})
					$.ajax({ 
						type: "GET", 
						url: "/manage/employee?id="+employee_id,
						contentType: "application/json; charset=utf-8", 
						dataType: "json", 
					}).done(update_employee_info);
				})
			};

			var update_employee_info = function(data){
				employee_info = data['result'][0]
				console.log(employee_info);
				console.log(employee_info["id"]);
				$('#employee_info_table').attr('data-employee-id',employee_info["id"]);
				$('#employee_info_name').text(employee_info['name']);
				$('#employee_info_position').text(employee_info['position']);
				$('#employee_info_inspection').text(employee_info['inspection']);
				$('#employee_info_inspection_date').text(employee_info['inspection_date']);
				$('#employee_info_assigned').text(employee_info['is_assigned']);

				for(each_idx in employee_info['assigned_room_list']){
					var room_num = employee_info['assigned_room_list']['each_idx']
					console.log('room_num'+room_num.toString())
					var index = to_assign_room_list.indexOf(room_num);
					if (index > -1) {
					    to_assign_room_list.splice(index, 1);
					}
					else{
						to_assign_room_list.push(room_num);
					}
				}
				$('#employee_info_rooms textarea').text(to_assign_room_list);
			};

			var assign_btn_click_listener = function(){
				$('#assign_send_btn').click(function(){
					console.log('click')
					var employee_id = $('#employee_info_table').attr('data-employee-id');
					console.log(employee_id);
					$.ajax({ 
						type: "POST", 
						url: "/manage/assign", data: JSON.stringify({"employee_id":employee_id,"room_list":to_assign_room_list }), 
						contentType: "application/json; charset=utf-8", 
						dataType: "json", 
						success: function(data){
							window.location.reload(); 
						}, 
						failure: function(errMsg) { 
							alert(errMsg)
						}
					});
				})
			};
			get_team_list.then(update_team_list).then(team_click_listner).then(assign_btn_click_listener);
		});
		 	

		$(".assign_box_x_btn").click(function(){
			$("#assign_room_box").fadeIn()
				.animate({opacity:0}, 500, function() {
				    $(this).css({display:'None'})
				    //callback
				});
				to_assign_room_list = []
				employee_list = []
			$(".assigned_room_overlay").unbind();	
			$(".assign_room_box *").unbind();
			$(".room_wrapper").css({marginBottom:0});
			$('.assign_check').css({'display':'none'});
			$(".assigned_room_overlay").css({'display':'none'});
			$(".inspected_room_overlay").css({'display':'none'});
			
		})


//ASSIGN INSPECTION ROOM
		$("#assign_inspection_room").click(function(){
			to_assign_room_list = []
			$("#assign_room_box").fadeIn()
				.css({display:'block'})
				.animate({opacity:1}, 500, function() {
				    //callback
			});

			$(".room_wrapper").css({marginBottom:284})
			$(".inspected_room_overlay").fadeIn().css({'display':'block'});
			console.log('css');
			$(".inspected_room_overlay").click(function(){
				console.log('click');
				$(this).children('.assign_check').toggle();
				var room_num = $(this).parent().attr('data-room-num');
				var index = to_assign_room_list.indexOf(room_num);
				if (index > -1) {
				    to_assign_room_list.splice(index, 1);
				}
				else{
					to_assign_room_list.push(room_num);
				}

				$('#employee_info_rooms textarea').text(to_assign_room_list);
			});

			var get_team_list =	$.ajax({ 
				type: "GET", 
				url: "/manage/teams",
				contentType: "application/json; charset=utf-8", 
				dataType: "json"
			});
			var update_team_list = function(data){
				var team_list_html = ''
				team_list = data['team_list']
				for(i in team_list){
					team_list_html += '<li class="assign_box_team_li">'+team_list[i]+'</li>\n'
				}
				$("#team_list ul").html(team_list_html);
			}

			function team_click_listner(){
				$(".assign_box_team_li").click(function(){

					$(".assign_box_team_li").each(function(){
						$(this).css({'backgroundColor':'#ffffff'})
					})
					$(this).css({'backgroundColor':'#d3eff9'})
					$.ajax({ 
						type: "GET", 
						url: "/manage/employee?team="+$(this).text(),
						contentType: "application/json; charset=utf-8", 
						dataType: "json", 
					}).then(update_employee_list).then(employee_click_listener);
				})
			};
			employee_list = []

			var update_employee_list = function(data){
				var employee_list_html = ''
				employee_list = data['result']

				for(i in employee_list){
					employee_list_html += '<li data-employee-id="'+employee_list[i]['id']+'">\
					<div class="employee_name">'+employee_list[i]['name']+'</div>\
					<div class="employee_assign">'+employee_list[i]['is_assigned']+'</div>\
					<div class="employee_room">'+employee_list[i]['assigned_room_list']+'</div>\
					</li>\n'
				}
				$("#assign_room_box #employee_list ul").empty();
				$("#assign_room_box #employee_list ul").append(employee_list_html);
			};


			function employee_click_listener(){
				$("#employee_list ul li").click(function(){
					var employee_id = $(this).attr("data-employee-id");
					$("#employee_list ul li").each(function(){
						$(this).css({'backgroundColor':'#ffffff'})	
					})
					$(this).css({'backgroundColor':'#d3eff9'})
					$.ajax({ 
						type: "GET", 
						url: "/manage/employee?id="+employee_id,
						contentType: "application/json; charset=utf-8", 
						dataType: "json", 
					}).done(update_employee_info);
				})
			};

			var update_employee_info = function(data){
				employee_info = data['result'][0]
				console.log(employee_info);
				console.log(employee_info["id"]);
				$('#employee_info_table').attr('data-employee-id',employee_info["id"]);
				$('#employee_info_name').text(employee_info['name']);
				$('#employee_info_position').text(employee_info['position']);
				$('#employee_info_inspection').text(employee_info['inspection']);
				$('#employee_info_inspection_date').text(employee_info['inspection_date']);
				$('#employee_info_assigned').text(employee_info['is_assigned']);

				for(each_idx in employee_info['assigned_room_list']){
					var room_num = employee_info['assigned_room_list']['each_idx']
					console.log('room_num'+room_num.toString())
					var index = to_assign_room_list.indexOf(room_num);
					if (index > -1) {
					    to_assign_room_list.splice(index, 1);
					}
					else{
						to_assign_room_list.push(room_num);
					}
				}
				$('#employee_info_rooms textarea').text(to_assign_room_list);
			};

			var assign_btn_click_listener = function(){
				$('#assign_send_btn').click(function(){
					console.log('click')
					var employee_id = $('#employee_info_table').attr('data-employee-id');
					console.log(employee_id);
					$.ajax({ 
						type: "POST", 
						url: "/manage/inspect", data: JSON.stringify({"employee_id":employee_id,"room_list":to_assign_room_list }), 
						contentType: "application/json; charset=utf-8", 
						dataType: "json", 
						success: function(data){
							window.location.reload(); 
						}, 
						failure: function(errMsg) { 
							alert(errMsg)
						}
					});
				})
			};
			get_team_list.then(update_team_list).then(team_click_listner).then(assign_btn_click_listener);
		});
		 	





		$("#delete_room").click(function(){

		    $(".delete_room_overlay").toggle();

		    //add room number to temp list
		    $(".delete_room_btn").click(function(){
				var room_num = $(".delete_room_form").val();
				room_list.push(room_num);
				$('.delete_room_list').empty();
				var room_code = ''
				for(i in room_list){
					room_code+='<li>'+room_list[i]+',</li>'
				}
				$('.delete_room_list').append(room_code);
			})
		    //submit temp room list
			$('.delete_room_submit').click(function(){
				$.ajax({ 
					type: "POST", 
					url: "/manage/delete_room", data: JSON.stringify({"room_list":room_list }), 
					contentType: "application/json; charset=utf-8", 
					dataType: "json", 
					success: function(data){
						console.log(data['result'])
						location.reload(); 
					}, 
					failure: function(errMsg) { 
						alert(errMsg)
					}
				});
			})
		});
			


		$("#add_room").click(function(){

		    $(".add_room_overlay").toggle();

		    //add room number to temp list
		    $(".add_room_btn").click(function(){
				var room_num = $(".add_room_form").val();
				room_list.push(room_num);
				$('.add_room_list').empty();
				var room_code = ''
				for(i in room_list){
					room_code+='<li>'+room_list[i]+'</li>'
				}
				$('.add_room_list').append(room_code);
			})
		    //submit temp room list
			$('.add_room_submit').click(function(){
				$.ajax({ 
					type: "POST", 
					url: "/manage/add_room", data: JSON.stringify({"room_list":room_list }), 
					contentType: "application/json; charset=utf-8", 
					dataType: "json", 
					success: function(data){
						console.log(data['result'])
						location.reload(); 
					}, 
					failure: function(errMsg) { 
						alert(errMsg)
					}
				});
			})
		});
			
		$(document).on("click", '.popup_x_btn',function(){
				room_list = []
				$(this).parent().parent().toggle();
		});

		var room_list = []
		

		$(document).on("click", '.popup_close_btn',function(){

				$(this).parent().parent().parent().toggle();
				$(this).parent().parent().empty();
		});

		$('.card').click(function(){
		if($("#assign_room_box").css('display') == 'none'){
			var room_num = $(this).attr("data-room-num");
			$.ajax({ 
				type: "GET", 
				url: "/manage/room/"+room_num.toString(), 
				contentType: "application/json; charset=utf-8", 
				dataType: "json", 
				success: function(data){
						var room = data['result']
						var add_room_popup = "\
					     <form action='/checkinout' method='post'>\
					     <div class='room_num_title'>Room "+room['number']+"</div>\
					     <input type='number' value="+room['number']+" name='room_num' style='display:none;'>\
					     <table class='room_info_table'>\
						     <tr>\
						     	<td>Room type</td><td><input type='text' value='"+room['room_type']+"' disabled></td>\
						     	<td>VIP</td><td><input type='text' id='isvip'></td>\
						     </tr>\
						     <tr>\
						     	<td>Room status</td><td><input type='text' disabled value='"+room['state']+"'></td>\
						     	<td>Name</td><td><input type='text' id='customer_name' name='customer' value='"+room['customer_name']+"'></td>\
						     </tr>\
						     <tr>\
						     	<td>Inspection</td><td><input type='text'></td>\
						     	<td>Supervisor</td><td><input type='text' name='supervisor'></td>\
						     </tr>\
						     <tr>\
						     	<td>Arrival</td><td><input type='text' id='datetimepicker_date_arr' name='date_arr'><div class='calendar_ic''></div></td>\
						     	<td>Departure</td><td><input type='text' id='datetimepicker_date_dep' name='date_dep'><div class='calendar_ic'></div></td>\
						     </tr>\
						     <tr>\
						     	<td>Arr. Time</td><td><input type='text' id='datetimepicker_time_arr' name='time_arr'></td>\
						     	<td>Dep. Time</td><td><input type='text' id='datetimepicker_time_dep' name='time_dep'></td>\
						     </tr>\
						     <tr>\
						     	<td></td>\
						     	<td>\
						     		<div class='checkin_btn'><div class='checkin_span'>Check in</div><div id='checkin_circle'></div></div>\
						     	</td>\
						     	<td></td>\
						     	<td>\
						     		<div class='checkout_btn'><div class='checkout_span'>Check out</div><div id='checkout_circle'></div></div>\
						     	</td>\
						     </tr>\
						     <tr>\
						     	<td id='room_info_notice_span'>notice</td><td colspan=3><textarea name='notice' cols='30' rows='8' id='room_info_notice' placeholder='"+room['notice']+"'></textarea></td>\
						     </tr>\
					     </table>\
					     <div class='popup_close_btn'>\
					 		<div>Close</div>\
					 	</div>\
					     <div class='checkinout_submit'>Submit</form>";


					 	$(".room_info_overlay .popup").append(add_room_popup);
					    $(".room_info_overlay").toggle();

					    $('#datetimepicker_date_arr').datetimepicker({value:room['arrival_date'],step:10});
					    $('#datetimepicker_date_dep').datetimepicker({value:room['departure_date'],step:10});
						$('#datetimepicker_time_arr').datetimepicker({value:room['checkin_time'],step:10});
						$('#datetimepicker_time_dep').datetimepicker({value:room['checkout_time'],step:10});

						//checked in
						if(room['is_checkin'] == true){
							$('#checkin_circle').css({'backgroundColor':'#19a1d1'});
						}
						//checked out
						if(room['is_checkout'] == true){
							$('#checkout_circle').css({'backgroundColor':'#19a1d1'});
						}
						console.log(room['arrival_date']);

					    $(".checkinout_submit").click(function(){
					    		var room_num = room['number'];
								var date_arr = $('#datetimepicker_date_arr').val();
								var date_dep = $('#datetimepicker_date_dep').val();
								var time_arr = $('#datetimepicker_time_arr').val();
								var time_dep = $('#datetimepicker_time_dep').val();
								var notice = $('#room_info_notice').val();
								var customer_name = $('#customer_name').val();
								var isvip = $('#isvip').val();

								console.log(date_arr);
								if(date_arr == ''){
									alert('fill arrival date');
									return;
								}
								if(date_dep == ''){
									alert('fill departure date');
									return;
								}
								// if(customer_name == ''){
								// 	alert('fill customer\'s name');
								// 	return;
								// }
								var checkinout = {'room_num':room_num,'date_arr':date_arr,'date_dep':date_dep,'time_arr':time_arr,'time_dep':time_dep,'notice':notice,'customer_name':customer_name,'isvip':isvip}

								$.ajax({ type: "POST", url: '/manage/checkinout', data: JSON.stringify({"checkinout": checkinout }), contentType: "application/json; charset=utf-8", dataType: "json", 
								success: function(data){ 
										console.log(data);
										window.location.reload();

								}, failure: function(errMsg) { alert("a");}});

								
					    });


						var d = new Date($.now());
						var month = d.getMonth()+1;
						var day = d.getDate();
						var hours = d.getHours();
						var minutes = d.getMinutes();

						var today_date = d.getFullYear() + '/' +
						    (month<10 ? '0' : '') + month + '/' +
						    (day<10 ? '0' : '') + day;

						var today_date_en = 
						    (day<10 ? '0' : '') + day+'/'+
						    (month<10 ? '0' : '') + month + '/' +
						    d.getFullYear() ;


						var today_time =(hours<10 ? '0' : '')  + month + 
							(minutes<10 ? '0' : '') + minutes;

						var today_datetime = today_date + ' ' + today_time

						$('#datetimepicker_time_arr').datetimepicker({
							datepicker:false,
							format:'H:i',
							step:5,
							minTime:today_time
						});
						$('#datetimepicker_date_arr').datetimepicker({
							yearOffset:222,
							lang:'en',
							timepicker:false,
							format:'d/m/Y',
							formatDate:'Y/m/d',
							startDate:	today_date,
							minDate:today_date, // yesterday is minimum date
							
						});

						$('#datetimepicker_time_dep').datetimepicker({
							datepicker:false,
							format:'H:i',
							step:5,
						});
						$('#datetimepicker_date_dep').datetimepicker({
							yearOffset:222,
							lang:'en',
							timepicker:false,
							format:'d/m/Y',
							formatDate:'Y/m/d',
							startDate:	today_date,
							minDate:today_date, // yesterday is minimum date
							
						});

						$('#checkin_circle').click(function(){
							$('#datetimepicker_date_arr').datetimepicker({value:today_date_en,step:10});
							$('#datetimepicker_time_arr').datetimepicker({value:today_time,step:10});
							$(this).css({'backgroundColor':'#19a1d1'});
						});
						$('#checkout_circle').click(function(){
							$('#datetimepicker_date_dep').datetimepicker({value:today_date_en,step:10});
							$('#datetimepicker_time_dep').datetimepicker({value:today_time,step:10});
							$(this).css({'backgroundColor':'#19a1d1'});
						});
					}, 
				failure: function(errMsg) { 
					alert(errMsg)
				}
			});
		}
		});
	});

