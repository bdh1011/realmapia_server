$(document).ready(function(){

		$("#mainLeft .subMenu").hover(
		  function() {
		    $( this ).css({"backgroundColor":"#d3eff9"})
		  }, function() {
		    $( this ).css({"backgroundColor":"#fff"})
		  }
		);

		$("#wrap> #manage> #main> #form_data_content .contentList").click(function(){
			var detailInfo = $(this).next("li");
			if($("#wrap> #manage> #main> #form_data_content .contentList> .item_description> img:hover").length==0)
				if(detailInfo.attr("class")=="itemDetail")
					if(detailInfo.is(":hidden")){
						detailInfo.slideDown("slow");
					}
					else{
						detailInfo.slideUp("slow");
					}
		});



		$('#add_form').click(function(){
			$(".add_form_input_wrapper").remove();
			var add_form_li = '\
				<li class="contentList add_form_input_wrapper">\
					<div class="item_num"></div>\
					<select class="item_form"><option selected value="short">short</option><option value="long">long</option></select>\
					<input type="text" class="item_description">\
					<div class="item_avg_point"></div>\
					<input class="item_total_point" type="number">\
					<div class="item_percent"></div>\
					<div id="add_form_submit">OK</div>\
				</li>'

			$("#form_list").append(add_form_li)
			$(".add_form_input_wrapper .item_form").focus();
			$('#add_form_submit').click(function(){
				var form_type = $('.add_form_input_wrapper .item_form').val();
				var form_description = $('.add_form_input_wrapper .item_description').val();
				var form_total_point = $('.add_form_input_wrapper .item_total_point').val();
				
				var form_list = $("#form_list").children('.item_form').val();
				console.log(form_list);

				var short_cnt = 0;
				var long_cnt = 0;
				$("#form_list div.item_form").each(function(){
				    if($(this).text() == 'short'){
				    	short_cnt+=1;
				    }
				    else{
				    	long_cnt+=1;
				    }
				})
				var form_num = 0
				if(form_type=='short'){
					form_num = short_cnt+1;
				}
				else{
					form_num = long_cnt+1;
				}
				console.log(short_cnt);
				console.log(long_cnt);

				$.ajax({ type: "POST", url: '/manage/form', contentType: "application/json; charset=utf-8", dataType: "json",
					data: JSON.stringify({"form_type":form_type,"form_num":form_num,"form_description":form_description,"form_total_point":form_total_point}), 
					success: function(data){ 

						var update_form_li =  "\
							<li class='contentList'>\
								<div class='item_num'>"+form_num+"</div>\
								<div class='item_form'>"+form_type+"</div>\
								<div class='item_description'>"+form_description+"</div>\
								<div class='item_avg_point'>0</div>\
								<div class='item_total_point'>"+form_total_point+"</div>\
								<div class='item_percent'>0</div>\
								<img class='form_data_delete_btn' src='/static/img/ic_delete.png'>\
								<img class='form_data_edit_btn' src='/static/img/ic_edit.png'>\
							</li>"
						$(".add_form_input_wrapper").remove();
						$("#form_list").append(update_form_li);
					;}, 
					failure: function(errMsg) { alert("already exist");}});
			})
		})



		
		$('.form_data_delete_btn').click(function(){
				var form = $(this).parent()
				var form_id = $(this).parent().attr("data-form-id");
				console.log(form_id);
				$.ajax({ type: "POST", url: '/manage/delete_form', contentType: "application/json; charset=utf-8", dataType: "json",
					data: JSON.stringify({"form_id":form_id}), 
					success: function(data){ 
						form.remove();
					},
					failure: function(errMsg) { alert("delete failed");}});


		});
		$('.form_data_edit_btn').click(function(){
				//var staff_id = $(this).parent().attr("data-staff-id");
				var form_id = $(this).parent().attr("data-form-id");
				var form_type = $(this).siblings(".item_form").innerHTML;
				var form_num = $(this).siblings(".item_num")[0].innerHTML;
				var form_description = $(this).siblings(".item_description").innerHTML;
				
				var form_total_point = $(this).siblings(".item_total_point").text();
				var edit_form_li = '\
				<li class="contentList add_form_input_wrapper" data-form-id="'+form_id+'">\
					<div class="item_num">'+form_num+'</div>\
					<select class="item_form">\
						<option selected value="short">short</option>\
						<option value="long">long</option>\
					</select>\
					<input type="text" class="item_description" value="'+form_description+'">\
					<div class="item_avg_point"></div>\
					<input class="item_total_point" type="number" value="'+form_total_point+'">\
					<div class="item_percent"></div>\
					<div id="add_form_submit">OK</div>\
				</li>'
					
				$(this).parent().after(edit_form_li)
				

				$('#add_form_submit').click(function(){
				//get team list
						
					var form_type = $(this).siblings(".item_form").val();
					var form_num = $(this).siblings(".item_num")[0].innerHTML;
					var form_description = $(this).siblings(".item_description").val();
					var form_total_point = $(this).siblings(".item_total_point").val();
					console.log('form_id'+form_id);
					$.ajax({ type: "POST", url: '/manage/edit_form', contentType: "application/json; charset=utf-8", dataType: "json",
					data: JSON.stringify({"form_id":form_id, "form_type":form_type,"form_num":form_num,"form_description":form_description,"form_total_point":form_total_point}), 
					success: function(data){ 
						var update_form_li =  "\
							<li class='contentList' data-form-id='"+form_id+"''>\
								<div class='item_num'>"+form_num+"</div>\
								<div class='item_form'>"+form_type+"</div>\
								<div class='item_description'>"+form_description+"</div>\
								<div class='item_avg_point'>0</div>\
								<div class='item_total_point'>"+form_total_point+"</div>\
								<div class='item_percent'>0</div>\
								<img class='form_data_delete_btn' src='/static/img/ic_delete.png'>\
								<img class='form_data_edit_btn' src='/static/img/ic_edit.png'>\
							</li>"
						$(".add_form_input_wrapper").after(update_form_li);
						$(".add_form_input_wrapper").remove();
					;}, 
					failure: function(errMsg) { alert("already exist");}});
				});
				$(this).parent().remove();
				
				

				//edit staff submit
				$('#edit_staff_submit').click(function(){
					var name_to = $('input.staff_name').val();
					var staff_position = $('select#staff_position option:selected').val();
					var staff_team = $('select#staff_team option:selected').val();
					var login_date = $('input.login_date').val();
					var inspect_score = $('input.inspect_score').val();
					var inspect_date = $('input.inspect_date').val();
					console.log(name_to);
					console.log(staff_position);
					console.log(staff_team);

					$.ajax({ type: "POST", url: '/manage/edit_staff', contentType: "application/json; charset=utf-8", dataType: "json",
						data: JSON.stringify({"staff_id":staff_id,"name_to": name_to, 'staff_position':staff_position,'staff_team':staff_team}), 
						success: function(data){ 
							var add_staff_li = "\
								<li class='each_staff_list' data-staff-id='"+staff_id+"'>\
								<div class='staff_name'>"+name_to+"</div>\
								<div class='position'>"+staff_position+"</div>\
								<div class='staff_team'>"+staff_team+"</div>\
								<div class='login_date'>"+login_date+"</div>\
								<div class='inspect_score'>"+inspect_score+"</div>\
								<div class='inspect_date'>"+inspect_date+"</div>\
								<img class='staff_delete_btn' src='{{url_for('static',filename='img/ic_remove.png')}}''>\
								<img class='staff_edit_btn' src='{{url_for('static',filename='img/ic_edit.png')}}'>\
								</li>"
							$("#edit_staff_list").after(add_staff_li);
							$("#edit_staff_list").remove();
						;}, 
						failure: function(errMsg) { alert("already exist");}});
				})
			})

			$('.staff_delete_btn').click(function(){
				var staff_id = $(this).parent().attr("data-staff-id");
				var this_staff_list = $(this).parent()
				
				$.ajax({ type: "POST", url: '/manage/delete_staff', contentType: "application/json; charset=utf-8", dataType: "json",
					data: JSON.stringify({"staff": staff_id}), 
					success: function(data){
						this_staff_list.remove();
					;}, 
					failure: function(errMsg) { alert("already exist");}});
			})



	});

