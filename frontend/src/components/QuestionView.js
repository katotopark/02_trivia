import React, { Component } from 'react'

import '../stylesheets/App.css'
import Question from './Question'
import Search from './Search'
import $ from 'jquery'

class QuestionView extends Component {
	constructor() {
		super()
		this.state = {
			categories: {},
			currentCategory: null,
			page: 1,
			questions: [],
			totalQuestions: 0,
		}
	}

	componentDidMount() {
		this.getQuestions()
	}

	componentDidUpdate(_, prevState) {
		if (prevState.page !== this.state.page) this.getQuestions()
	}

	getQuestions = async () => {
		try {
			const {
				categories,
				current_category,
				questions,
				total_questions,
			} = await $.ajax({
				url: `/questions?page=${this.state.page}`,
				type: 'GET',
			})
			this.setState({
				categories: this.mapCategories(categories),
				currentCategory: current_category,
				questions,
				totalQuestions: total_questions,
			})
		} catch (error) {
			alert('Unable to load questions. Please try your request again')
		}
	}

	mapCategories = (categories) => {
		return categories.reduce((acc, { id, type }) => {
			acc[id] = type
			return acc
		}, {})
	}

	selectPage(num) {
		this.setState(() => ({
			page: num,
		}))
	}

	createPagination() {
		let pageNumbers = []
		let maxPage = Math.ceil(this.state.totalQuestions / 10)
		for (let i = 1; i <= maxPage; i++) {
			pageNumbers.push(
				<span
					key={i}
					className={`page-num ${i === this.state.page ? 'active' : ''}`}
					onClick={() => this.selectPage(i)}
				>
					{i}
				</span>
			)
		}
		return pageNumbers
	}

	getByCategory = (id) => {
		$.ajax({
			url: `/categories/${id}/questions`,
			type: 'GET',
			success: (result) => {
				this.setState({
					questions: result.questions,
					totalQuestions: result.total_questions,
					currentCategory: result.current_category,
				})
				return
			},
			error: (error) => {
				alert('Unable to load questions. Please try your request again')
				return
			},
		})
	}

	submitSearch = (searchTerm) => {
		$.ajax({
			url: '/questions/search',
			type: 'POST',
			dataType: 'json',
			contentType: 'application/json',
			data: JSON.stringify({ search_term: searchTerm }),
			xhrFields: {
				withCredentials: true,
			},
			crossDomain: true,
			success: (result) => {
				this.setState({
					questions: result.questions,
					totalQuestions: result.total_questions,
					currentCategory: result.current_category,
				})
				return
			},
			error: (error) => {
				alert('Unable to load questions. Please try your request again')
				return
			},
		})
	}

	questionAction = (id) => (action) => {
		if (action === 'DELETE') {
			if (window.confirm('are you sure you want to delete the question?')) {
				$.ajax({
					url: `/questions/${id}`,
					type: 'DELETE',
					success: (result) => {
						this.getQuestions()
					},
					error: (error) => {
						alert('Unable to load questions. Please try your request again')
						return
					},
				})
			}
		}
	}

	render() {
		const { categories, questions } = this.state
		return (
			<div className='question-view'>
				<div className='categories-list'>
					<h2
						onClick={() => {
							this.getQuestions()
						}}
					>
						Categories
					</h2>
					<ul>
						{Object.keys(categories).map((id) => (
							<li key={id} onClick={() => this.getByCategory(id)}>
								{categories[id]}
								<img className='category' src={`${categories[id]}.svg`} />
							</li>
						))}
					</ul>
					<Search submitSearch={this.submitSearch} />
				</div>
				<div className='questions-list'>
					<h2>Questions</h2>
					{questions &&
						questions.map(({ answer, category, difficulty, id, question }) => (
							<Question
								key={id}
								question={question}
								answer={answer}
								category={categories[category]}
								difficulty={difficulty}
								questionAction={this.questionAction(id)}
							/>
						))}
					<div className='pagination-menu'>{this.createPagination()}</div>
				</div>
			</div>
		)
	}
}

export default QuestionView
