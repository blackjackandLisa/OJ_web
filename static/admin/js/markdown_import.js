(function() {
    'use strict';
    
    // 防止重复初始化
    if (window.markdownImportInitialized) {
        console.log('Markdown导入脚本已经初始化，跳过重复加载');
        return;
    }
    window.markdownImportInitialized = true;
    
    // 等待jQuery和Bootstrap完全加载
    function initMarkdownImport() {
        // 检查jQuery是否可用
        if (typeof $ === 'undefined') {
            console.log('jQuery未加载，等待中...');
            setTimeout(initMarkdownImport, 100);
            return;
        }
        
        // 检查Bootstrap是否可用
        if (typeof $.fn.modal === 'undefined') {
            console.log('Bootstrap未加载，等待中...');
            setTimeout(initMarkdownImport, 100);
            return;
        }
        
        console.log('Markdown导入脚本开始加载...');
        console.log('jQuery版本:', $.fn.jquery);
        console.log('Bootstrap modal方法存在:', typeof $.fn.modal);
        
        // 添加导入按钮
        addImportButton();
        
        // 创建导入模态框
        createImportModal();
        
        console.log('Markdown导入脚本加载完成');
    }
    
    // 等待DOM就绪
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMarkdownImport);
    } else {
        initMarkdownImport();
    }
    
    function addImportButton() {
        // 检查是否已经有按钮了
        if ($('#markdown-import-btn').length > 0) {
            console.log('导入按钮已存在');
            return;
        }
        
        // 在表单上方添加导入按钮
        var $form = $('.problem-form, #problem_form, form');
        var $container = $('#markdown-import-container');
        
        // 调试信息
        console.log('查找表单元素:', $form.length);
        console.log('查找容器元素:', $container.length);
        console.log('当前页面URL:', window.location.href);
        
        var $button = $('<button type="button" class="default" id="markdown-import-btn" style="margin-bottom: 20px;">' +
                       '<i class="fas fa-file-import"></i> 从Markdown导入</button>');
        
        // 优先使用容器，否则插入到表单前
        if ($container.length > 0) {
            $container.append($button);
            console.log('导入按钮已添加到容器中');
        } else if ($form.length > 0) {
            $button.insertBefore($form.first());
            console.log('导入按钮已添加到表单前');
        } else {
            // 如果找不到表单，添加到页面顶部
            $button.prependTo('body');
            console.log('导入按钮已添加到页面顶部');
        }
    }
    
    function createImportModal() {
        var modalHtml = `
            <div class="modal fade" id="markdownImportModal" tabindex="-1" role="dialog" aria-labelledby="markdownImportModalLabel" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1050;">
                <div class="modal-dialog modal-lg" role="document" style="position: relative; width: 90%; max-width: 800px; margin: 50px auto;">
                    <div class="modal-content" style="background-color: white; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <div class="modal-header" style="padding: 15px; border-bottom: 1px solid #ddd; background-color: #f8f8f8;">
                            <h5 class="modal-title" id="markdownImportModalLabel" style="margin: 0; font-size: 16px; font-weight: bold;">从Markdown导入题目</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close" style="position: absolute; right: 15px; top: 15px; background: none; border: none; font-size: 20px; cursor: pointer;">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body" style="padding: 20px;">
                            <div class="form-group" style="margin-bottom: 15px;">
                                <label for="markdownText" style="display: block; margin-bottom: 5px; font-weight: bold;">粘贴Markdown文本：</label>
                                <textarea id="markdownText" class="form-control" rows="15" 
                                         placeholder="请粘贴完整的题目Markdown文本..." 
                                         style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 3px; font-family: monospace; resize: vertical;"></textarea>
                            </div>
                            <div id="parseResult" style="display: none; margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
                                <h6 style="margin-bottom: 10px; font-weight: bold;">解析结果预览：</h6>
                                <div id="previewContent" style="background-color: #f9f9f9; border: 1px solid #ddd; padding: 15px; border-radius: 3px; max-height: 400px; overflow-y: auto;"></div>
                            </div>
                        </div>
                        <div class="modal-footer" style="padding: 15px; border-top: 1px solid #ddd; background-color: #f8f8f8; text-align: right;">
                            <button type="button" class="default" data-dismiss="modal" style="margin-right: 10px;">取消</button>
                            <button type="button" class="default" id="parseMarkdownBtn">解析</button>
                            <button type="button" class="default" id="applyMarkdownBtn" style="display: none; margin-left: 10px;">应用到表单</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(modalHtml);
        
        // 绑定事件 - 使用事件委托，但只绑定一次
        if (!window.markdownImportEventsBound) {
            $(document).on('click', '#markdown-import-btn', function() {
                console.log('导入按钮被点击');
                $('#markdownImportModal').modal('show');
            });
            
            $(document).on('click', '#parseMarkdownBtn', function() {
                console.log('解析按钮被点击');
                parseMarkdown();
            });
            
            $(document).on('click', '#applyMarkdownBtn', function() {
                console.log('应用按钮被点击');
                applyToForm();
            });
            
            window.markdownImportEventsBound = true;
            console.log('事件监听器已绑定');
        }
    }
    
    function parseMarkdown() {
        var markdownText = $('#markdownText').val().trim();
        
        if (!markdownText) {
            alert('请先输入Markdown文本');
            return;
        }
        
        $('#parseMarkdownBtn').prop('disabled', true).text('解析中...');
        
        // 获取当前页面的基础URL
        var baseUrl = window.location.pathname;
        if (baseUrl.endsWith('/add/')) {
            baseUrl = baseUrl.replace('/add/', '/');
        }
        var apiUrl = baseUrl + 'parse-markdown/';
        
        console.log('API URL:', apiUrl);
        console.log('Markdown文本长度:', markdownText.length);
        
        $.ajax({
            url: apiUrl,
            type: 'POST',
            data: {
                'markdown_text': markdownText
            },
            success: function(response) {
                console.log('解析响应:', response);
                if (response.success) {
                    showParseResult(response.data);
                    $('#applyMarkdownBtn').show();
                } else {
                    console.error('解析失败:', response.error);
                    alert('解析失败: ' + (response.error || '未知错误'));
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX错误:', xhr, status, error);
                console.error('响应文本:', xhr.responseText);
                var errorMsg = '解析失败';
                try {
                    var response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch (e) {
                    errorMsg = '网络错误或服务器错误: ' + xhr.status;
                }
                alert(errorMsg);
            },
            complete: function() {
                $('#parseMarkdownBtn').prop('disabled', false).text('解析');
            }
        });
    }
    
    function showParseResult(data) {
        var previewHtml = `
            <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px;">标题:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 20px;">
                        ${data.title || '(未解析到)'}
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px;">难度:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 20px;">
                        ${data.difficulty || '(未解析到)'}
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px;">时间限制:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 20px;">
                        ${data.time_limit}ms
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px;">内存限制:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 20px;">
                        ${data.memory_limit}MB
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px; margin-top: 8px;">题目描述:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 60px; max-height: 120px; overflow-y: auto;">
                        ${data.description ? data.description.substring(0, 500) + (data.description.length > 500 ? '...' : '') : '(未解析到)'}
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px; margin-top: 8px;">输入格式:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 40px;">
                        ${data.input_format || '(未解析到)'}
                    </div>
                </div>
                
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <label style="width: 100px; font-weight: bold; margin-right: 10px; margin-top: 8px;">输出格式:</label>
                    <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 40px;">
                        ${data.output_format || '(未解析到)'}
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h6 style="margin-bottom: 15px; color: #333; font-weight: bold; border-bottom: 1px solid #ddd; padding-bottom: 5px;">输入输出样例:</h6>
                ${data.test_cases && data.test_cases.length > 0 ? 
                    data.test_cases.map((testCase, index) => `
                        <div style="margin-bottom: 15px; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">
                            <div style="display: flex; align-items: flex-start; margin-bottom: 8px;">
                                <label style="width: 80px; font-weight: bold; margin-right: 10px; margin-top: 8px;">样例输入 ${index + 1}:</label>
                                <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 30px; font-family: monospace;">
                                    ${testCase[0]}
                                </div>
                            </div>
                            <div style="display: flex; align-items: flex-start;">
                                <label style="width: 80px; font-weight: bold; margin-right: 10px; margin-top: 8px;">样例输出 ${index + 1}:</label>
                                <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 30px; font-family: monospace;">
                                    ${testCase[1]}
                                </div>
                            </div>
                        </div>
                    `).join('') :
                    `
                        <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                            <label style="width: 100px; font-weight: bold; margin-right: 10px; margin-top: 8px;">样例输入:</label>
                            <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 40px; font-family: monospace;">
                                ${data.sample_input || '(未解析到)'}
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                            <label style="width: 100px; font-weight: bold; margin-right: 10px; margin-top: 8px;">样例输出:</label>
                            <div style="flex: 1; padding: 8px; border: 1px solid #ccc; background-color: white; min-height: 40px; font-family: monospace;">
                                ${data.sample_output || '(未解析到)'}
                            </div>
                        </div>
                    `
                }
            </div>
            
            </div>
        `;
        
        $('#previewContent').html(previewHtml);
        $('#parseResult').show();
        
        // 保存解析结果到全局变量
        window.parsedProblemData = data;
    }
    
    function applyToForm() {
        if (!window.parsedProblemData) {
            alert('没有可应用的数据');
            return;
        }
        
        var data = window.parsedProblemData;
        
        // 填充表单字段
        fillField('id_title', data.title);
        fillField('id_description', data.description);
        fillField('id_input_format', data.input_format);
        fillField('id_output_format', data.output_format);
        
        // 处理多个样例输入输出
        if (data.test_cases && data.test_cases.length > 0) {
            // 如果有多个测试用例，将它们组合起来
            var combinedInput = data.test_cases.map((testCase, index) => {
                return data.test_cases.length > 1 ? 
                    `样例输入 ${index + 1}:\n${testCase[0]}` : 
                    testCase[0];
            }).join('\n\n');
            
            var combinedOutput = data.test_cases.map((testCase, index) => {
                return data.test_cases.length > 1 ? 
                    `样例输出 ${index + 1}:\n${testCase[1]}` : 
                    testCase[1];
            }).join('\n\n');
            
            fillField('id_sample_input', combinedInput);
            fillField('id_sample_output', combinedOutput);
        } else {
            // 如果没有测试用例，使用原始的单个样例
            fillField('id_sample_input', data.sample_input);
            fillField('id_sample_output', data.sample_output);
        }
        
        fillField('id_hint', data.hint);
        fillField('id_time_limit', data.time_limit);
        fillField('id_memory_limit', data.memory_limit);
        
        // 设置难度
        if (data.difficulty) {
            var difficultyMap = {
                '简单': 'easy',
                '中等': 'medium', 
                '困难': 'hard'
            };
            var difficultyValue = difficultyMap[data.difficulty] || 'easy';
            $('#id_difficulty').val(difficultyValue);
        }
        
        // 自动创建测试用例
        createTestCases(data.test_cases);
        
        // 关闭模态框
        $('#markdownImportModal').modal('hide');
        
        alert('题目信息已成功导入到表单中！');
    }
    
    function fillField(fieldId, value) {
        var $field = $('#' + fieldId);
        if ($field.length > 0 && value) {
            if ($field.is('textarea')) {
                $field.val(value);
            } else if ($field.is('input')) {
                $field.val(value);
            } else if ($field.is('select')) {
                $field.val(value);
            }
        }
    }
    
    function createTestCases(testCases) {
        console.log('开始创建测试用例，数量:', testCases.length);
        
        // 清除现有的测试用例
        $('.inline-related').each(function() {
            var $this = $(this);
            if ($this.find('input[name$="-input"]').length > 0) {
                var $deleteCheckbox = $this.find('input[name$="-DELETE"]');
                if ($deleteCheckbox.length > 0) {
                    $deleteCheckbox.prop('checked', true);
                }
            }
        });
        
        // 添加新的测试用例
        testCases.forEach(function(testCase, index) {
            console.log(`创建测试用例 ${index + 1}:`, testCase);
            
            // 点击"添加另一个"按钮
            var $addButton = $('.add-row a');
            if ($addButton.length > 0) {
                $addButton.click();
                
                // 等待新行添加完成，使用更长的延迟确保DOM更新
                setTimeout(function() {
                    var $newRow = $('.inline-related').last();
                    console.log('找到新行:', $newRow.length);
                    
                    // 查找输入和输出字段
                    var $inputField = $newRow.find('input[name$="-input"], textarea[name$="-input"]');
                    var $outputField = $newRow.find('input[name$="-output"], textarea[name$="-output"]');
                    
                    console.log('输入字段:', $inputField.length, '输出字段:', $outputField.length);
                    
                    if ($inputField.length > 0) {
                        $inputField.val(testCase[0]);
                        console.log('设置输入:', testCase[0]);
                    }
                    if ($outputField.length > 0) {
                        $outputField.val(testCase[1]);
                        console.log('设置输出:', testCase[1]);
                    }
                    
                    // 如果是第一个测试用例，标记为样例
                    if (index === 0) {
                        var $sampleCheckbox = $newRow.find('input[name$="-is_sample"]');
                        if ($sampleCheckbox.length > 0) {
                            $sampleCheckbox.prop('checked', true);
                            console.log('标记第一个测试用例为样例');
                        }
                    }
                }, 200 * (index + 1)); // 递增延迟，确保每个测试用例都能正确添加
            } else {
                console.log('未找到添加按钮');
            }
        });
        
        console.log('测试用例创建完成');
    }
    
})(django.jQuery);
