# Methods added to this helper will be available to all templates in the application.
module ApplicationHelper
  def format(text)
    if text != nil
      text = text.gsub(/<\/?[^>]*>/, "")
      BlueCloth::new(text).to_html
    end
  end
  
  def clean(text)
    if text != nil
      text = text.gsub(/<\/?[^>]*>/, "")
    end
  end
  
  def pagetitle(text)
    c = controller.controller_name
    a = controller.action_name
    i = params[:id]

    if c == 'items'
      if a == 'list'
        @pagetitle = 'Marathon ' + @pagetitle if i == 'Marathon'
      end
    end
    
    @pagetitle = text
    @pagetitle = "Marathon Aleph One community downloads." if current_page?('/')
    text
    
    text
  end
  
  def subtitle
    c = params[:controller]
    a = params[:action]
    subtitle = "Items " + a + ":" + c
    
    if c == 'items' and a == 'index'
      subtitle = "Items"
      subtitle = "Latest Updates and Submissions" if !params[:order]
    elsif c == 'items' and a == 'show'
      subtitle = Item.find_by_permalink(params[:id]).name
      @pagetitle = subtitle +' '+ @pagetitle
    elsif c == 'tags' and a == 'show'
      subtitle = "Tagged '" + params[:id].capitalize + "'"
      @pagetitle = (params[:id].capitalize) +' '+ @pagetitle
    end
    
    if params[:order]
      subtitle += order_name(params[:order])
    end
    
    subtitle
  end
  
  def order_name(txt)
    name = " by "
    
    case txt
      when 'new'
        name += "Latest Updates"
      when 'old'
        name += "Oldest Updates"
      when 'best'
        name += "Best Reviewed"
      when 'worst'
        name = ""
      when 'popular'
        name += "Most Downloads"
      when 'unpopular'
        name += "Fewest Downloads"
      when 'day'
        name += "Daily Downloads"
      when 'week'
        name += "Weekly Downloads"
      when 'month'
        name += "Monthly Downloads"
      when 'loud'
        name += "Most Reviews"
      when 'quiet'
        name += "Fewest Reviews"
    end
    
    name
  end
  
end
